# Arquitetura proposta

## Decisão resumida

O MVP será local-first, orientado por arquivos e dividido em um núcleo Python, ferramentas FFmpeg/FFprobe e um adapter Node/HyperFrames. Não haverá banco de dados, painel web, publicação automática ou backend de IA obrigatório.

## Princípios de desenho

1. Originais são imutáveis; toda transformação usa cópia de trabalho.
2. Cada artefato deriva de entrada, configuração e versão identificáveis.
3. Conteúdo editorial é separado de apresentação.
4. Providers são trocáveis por interfaces estreitas.
5. Renders preliminar e final são comandos e permissões distintos.
6. Aprovação humana vincula hashes dos artefatos revisados.
7. Rede e serviços externos ficam desabilitados por padrão.
8. Um job pode ser executado interativamente hoje e por worker amanhã.

## Limites dos runtimes

### Python

Responsável por:

- CLI e casos de uso;
- estado do projeto;
- ingestão, checksum e cópia;
- FFprobe e validação técnica;
- extração e análise de áudio;
- providers de transcrição e análise editorial;
- geração de transcript, SRT/ASS e edit plan;
- validação JSON Schema;
- políticas de segurança e aprovação;
- logs, manifestos e relatórios.

Versão proposta para a Fase 1: Python 3.12 em `.venv`, com lockfile. A versão 3.14 instalada pode continuar no host, mas não será a base oficial até que todas as dependências sejam testadas.

### Node/HyperFrames

Responsável por:

- templates em movimento;
- lower third, logo, encerramento e elementos de marca;
- preview;
- lint e validação estrutural;
- inspeção de layout e contraste em Chrome headless;
- render de camadas visuais quando necessário.

Versão proposta: Node 24 LTS fixado no projeto. Node 25.9.0 do host está EOL. HyperFrames deverá ser dependência local com versão exata, nunca dependência global implícita.

### FFmpeg/FFprobe

Responsáveis por:

- probe;
- proxy;
- extração e normalização de áudio;
- detecção de silêncio;
- cortes e concatenação;
- scale/crop/pad;
- composição final de mídia e áudio;
- legendas incorporadas;
- codecs de entrega.

A build deve ser resolvida por configuração e validada no início de cada execução. O manifesto registra caminho, versão, configuração e comando sanitizado.

## Componentes lógicos

```text
CLI / Worker entrypoint
        |
Application use cases
        |
Domain: project, state machine, approvals, policies
        |
Ports
  +-----+----------------+----------------+----------------+
  |                      |                |                |
StorageProvider   TranscriptionProvider  RenderProvider  EditorialProvider
  |                      |                |                |
Local filesystem  FasterWhisper/OpenAI   FFmpeg +       Local/manual,
                                      HyperFrames       future API
```

Os adapters não alteram o domínio. Cada execução recebe um `job.json` normalizado e devolve `result.json` com status, artefatos, checksums, avisos e erro acionável.

## Formatos canônicos

- YAML: configuração humana e metadados editáveis, como `project.yaml`.
- JSON: artefatos de máquina, contratos entre processos e manifestos.
- JSON Schema 2020-12: validação dos JSON e da representação normalizada de YAML.
- JSONL: eventos de auditoria append-only.
- SRT/VTT: distribuição e revisão simples.
- ASS: legenda incorporada com controle visual.
- UTF-8 sem BOM: codificação padrão.
- segundos decimais no JSON: timecodes canônicos; conversão para frames ocorre apenas na borda do render.

Todos os schemas terão `schema_version`. Campos desconhecidos serão rejeitados nos contratos críticos e tolerados apenas onde uma extensão for explicitamente permitida.

## Layout proposto do código na Fase 1

```text
src/inova_av/
  cli/
  application/
  domain/
  ports/
  adapters/
    ffmpeg/
    filesystem/
    transcription/
    hyperframes/
  schemas/
  observability/
hyperframes/
  compositions/
  components/
  tests/
schemas/
tests/
```

Essa pequena adaptação à estrutura original torna explícitos domínio, portas e adapters. As áreas funcionais continuam representadas por módulos, mas sem criar pacotes vazios antecipadamente.

## Estado e retomada

O estado é uma máquina explícita. Uma etapa:

1. valida pré-condições;
2. calcula a chave de execução a partir de hashes e configuração;
3. reutiliza saída válida ou escreve em diretório temporário;
4. valida o resultado;
5. move atomicamente o artefato para o destino;
6. registra evento e atualiza o estado.

Falhas não apagam intermediários válidos. Nova execução retoma a partir do último artefato validado. Mudança de entrada ou configuração invalida apenas dependentes.

## Gate de aprovação

`approval.json` deverá registrar:

- projeto e versão;
- identidade do revisor;
- data e fuso;
- hashes de transcript revisado, edit plan, captions, template e preview;
- estado de autorização de imagem;
- checklist obrigatório;
- decisão e observações.

O comando de render final encerra com erro se qualquer hash mudou, se uma autorização crítica estiver pendente, se o asset não estiver licenciado ou se o estado não for `approved`. Não haverá `--force` no MVP.

## Identidade visual

Antes da primeira composição, a equipe deverá aprovar `DESIGN.md` com cores, tipografia, motion rules, áreas seguras e proibições. HyperFrames não deverá usar cores, fontes ou logos genéricos. `assets/registry.yaml` registrará origem, checksum, licença, restrições e aprovação de cada asset.

## Modo A e Modo B

### Modo A

O CLI executa localmente e pausa nos gates. Análise editorial pode ser preparada para revisão humana. Não exige API.

### Modo B

Um worker recebe o mesmo `job.json`, usa os mesmos casos de uso e grava os mesmos artefatos. n8n ou outra fila somente agenda jobs e consulta resultados; não contém regra editorial nem credencial dentro dos arquivos do projeto.

## Offline

Após provisionar dependências, browser, modelos, fontes e assets, ingestão, transcrição local, análise técnica, edição, preview e render devem funcionar sem internet. O modo offline falhará cedo se a configuração selecionar provider remoto ou se algum recurso não estiver no cache, sem tentar egress silencioso.

## Exportação futura para NLE

O edit plan já preserva arquivo, in/out, timebase e transcript excerpt. Isso permite gerar EDL ou FCPXML posteriormente. A Fase 1 apenas definirá o contrato; a exportação completa fica fora do MVP até validar round-trip com o editor escolhido.
