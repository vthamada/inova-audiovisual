# Plano de implementação — Fase 1

Status em 2026-07-29: implementação local concluída; CI remoto e validação humana do handoff permanecem pendentes. Evidência em `phase-1-verification.md`.

## Objetivo

Criar a fundação técnica do repositório, sem implementar ingestão, transcrição ou render audiovisual completos. Ao final, o projeto deverá possuir estrutura mínima, ambientes reproduzíveis, contratos, CLI de diagnóstico, logs, testes e documentação suficiente para autorizar a Fase 2.

## Pré-condições humanas

Antes de iniciar:

- aprovar ADR-0001 a ADR-0004;
- confirmar Python 3.12 e Node 24 LTS;
- aceitar `faster-whisper` como hipótese sujeita a benchmark;
- aceitar FFmpeg + HyperFrames como motores coordenados;
- nomear quem pode aprovar versões;
- fornecer ou indicar processo para obter assets oficiais;
- decidir a política inicial de retenção e mídia fora do Git.

## Entregáveis

### Governança e documentação

- `README.md`: propósito, limites, quick start e status das fases;
- `AGENTS.md`: regras locais, gates e comandos seguros;
- `DESIGN.md`: inicialmente um gate explícito “aguardando assets” ou identidade aprovada; nenhuma composição antes da aprovação;
- `SECURITY.md`: reporte, segredos, dados e egress;
- `docs/operations/environment-setup.md`;
- `docs/operations/troubleshooting.md`;
- registro de assets e licenças vazio, mas validável;
- ADRs atualizados para `Aceito` ou `Rejeitado`.

### Ambientes

- `.python-version` ou equivalente para Python 3.12;
- `.venv` ignorado;
- `pyproject.toml` com pacote, CLI, lint, tipos e testes;
- lockfile Python;
- `.nvmrc`/`.node-version` para Node 24 LTS;
- `package.json` e lockfile npm;
- HyperFrames com versão exata local;
- `.env.example` sem segredo;
- script PowerShell de diagnóstico;
- política explícita para FFmpeg e Chrome Headless Shell.

### Estrutura

```text
config/
assets/
docs/
schemas/
src/inova_av/
  cli/
  application/
  domain/
  ports/
  adapters/
  observability/
hyperframes/
tests/
  unit/
  integration/
  fixtures/
  golden/
workspace/
scripts/
```

Diretórios vazios só serão mantidos quando acompanhados por README/placeholder com finalidade. Mídia e outputs permanecerão ignorados.

### Contratos

Schemas JSON 2020-12 para:

- project;
- transcript;
- edit plan;
- render manifest;
- approval;
- audit event;
- asset registry;
- render request/result.

Também serão definidos:

- enums de estados e transições;
- formato de erro;
- códigos de saída da CLI;
- política de versão de schema;
- normalização YAML → JSON;
- regras de timecode e caminhos relativos.

### CLI mínima

Comandos previstos:

```text
inova-av --version
inova-av doctor [--json]
inova-av schema validate <tipo> <arquivo>
inova-av project validate <diretório>
inova-av config show
```

O CLI não processará mídia na Fase 1. `doctor` somente inspeciona e reporta Git opcional, Python, Node, FFmpeg, FFprobe, HyperFrames, browser, CPU, GPU, RAM, disco e configuração.

## Sequência de trabalho

### 1. Baseline do repositório — complexidade baixa

- revisar e aceitar/rejeitar ADRs;
- criar `.gitignore` abrangente;
- criar README, AGENTS, SECURITY e estrutura;
- definir convenções de nomes, UTF-8 e caminhos;
- confirmar que nenhum asset ou mídia entra no Git.

Verificação: árvore esperada, `git check-ignore` para amostras e busca por segredos.

### 2. Toolchain Python — complexidade média

- provisionar Python 3.12 lado a lado, sem remover a instalação 3.14;
- criar `.venv`;
- configurar build e CLI;
- selecionar lint/format/type check;
- fixar dependências e lock;
- adicionar testes mínimos.

Verificação: instalação limpa no venv, `--version`, lint, tipos e testes em PowerShell com caminho contendo espaços.

### 3. Toolchain Node/HyperFrames — complexidade média

- fixar Node 24 LTS;
- criar `package.json`;
- adicionar HyperFrames em versão exata;
- provisionar Chrome Headless Shell pelo comando oficial;
- desabilitar telemetria;
- criar scripts npm apenas de diagnóstico/validação, sem composição de marca;
- testar `doctor`.

Verificação: `npm ci`, `hyperframes doctor`, execução offline após cache e inventário de arquivos baixados.

### 4. Política FFmpeg — complexidade média

- escolher uma build suportada e versionada;
- remover ambiguidade lógica entre instalações por resolução explícita;
- validar codecs e filtros mínimos;
- executar smoke tests `libx264` e `h264_qsv`;
- registrar caminho e build.

Não é necessário desinstalar builds do host. O projeto deve falhar se resolver uma versão não aceita.

### 5. Domínio e schemas — complexidade alta

- modelar IDs, estados, timecodes, hashes e aprovações;
- escrever schemas e exemplos válidos/inválidos;
- implementar validação sem I/O de mídia;
- implementar transições puras;
- implementar canonicalização para hashing.

Verificação: unit tests, property-based tests para timecodes/caminhos e snapshots de erros.

### 6. Portas e contratos de processo — complexidade média

- declarar protocols/interfaces de storage, transcription, editorial e render;
- definir request/result e exit codes;
- criar adapters “noop/fake” para testes;
- garantir que nenhum provider real seja chamado na Fase 1.

Verificação: contract tests com fakes e JSON fixtures.

### 7. Observabilidade — complexidade média

- logs humanos e JSON;
- `run_id`, correlação e duração;
- redaction de segredos/PII;
- erro tipado e acionável;
- manifesto do `doctor`.

Verificação: golden logs sem segredo e comportamento consistente em erro.

### 8. CI e segurança — complexidade média

- workflow para lint, tipos, testes e schemas;
- matriz Windows obrigatória; Linux como compatibilidade inicial;
- audit de dependências;
- secret scanning;
- limite de tamanho de arquivo;
- nenhum download de modelo ou browser durante testes unitários.

Verificação: CI passa em checkout limpo e falha em fixture propositalmente inválida.

### 9. Documentação e handoff — complexidade baixa

- instalar do zero seguindo somente o README;
- registrar limitações reais;
- atualizar diagnóstico;
- preparar relatório para autorizar Fase 2.

## Estratégia de testes da Fase 1

### Unitários

- IDs e nomes seguros;
- parsing e formatação de timecode;
- aritmética racional de duração;
- máquina de estados;
- canonicalização e hashing;
- validação de configuração;
- políticas de aprovação;
- redaction de logs;
- resolução de caminhos sob a raiz.

### Contrato

- schemas aceitam exemplos válidos;
- rejeitam campos/estados/timecodes inválidos;
- render request/result permanece compatível;
- provider fake satisfaz a mesma interface.

### Integração

- `doctor` encontra ferramentas;
- FFmpeg/FFprobe executam smoke test sintético;
- `npx.cmd` é usado no Windows;
- HyperFrames doctor reconhece browser provisionado;
- ambiente funciona com caminho contendo espaços;
- modo offline não tenta rede.

### Segurança

- path traversal bloqueado;
- symlink/reparse point fora da raiz bloqueado;
- segredo é mascarado;
- mídia e `.env` são ignorados;
- alteração de hash invalida aprovação;
- subprocessos não usam shell.

## Critérios de saída

A Fase 1 pode ser marcada como concluída somente quando:

- ADRs estiverem aprovados;
- ambientes forem reproduzíveis em checkout limpo;
- todas as ferramentas obrigatórias passarem no `doctor`;
- schemas e máquina de estados tiverem testes;
- CLI mínima funcionar em Windows;
- logs e erros forem acionáveis;
- gate de aprovação tiver testes de contrato;
- CI passar;
- documentação for executada por outra pessoa;
- nenhuma mídia real, publicação ou provider externo tiver sido acionado.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Python 3.12 não disponível no host | instalação lado a lado e venv; não alterar Python global |
| Node do host está EOL | fixar Node 24 LTS |
| duas builds FFmpeg | resolver caminho explicitamente e validar build |
| browser HyperFrames ausente | provisionar e fixar antes de render |
| dependências grandes | separar extras e caches; medir disco |
| schema excessivo cedo | começar pelos campos obrigatórios e versionar |
| mídia entrar no Git | ignore, hook/CI e limite de tamanho |
| telemetria | desabilitar e verificar antes de material real |
| aprovação nominal indefinida | bloquear conclusão até papéis serem definidos |

## O que não fazer na Fase 1

- não ingerir acervo real;
- não baixar modelos de transcrição como efeito de testes;
- não criar composição com identidade genérica;
- não renderizar versão institucional;
- não integrar Drive, n8n, WordPress ou redes sociais;
- não implementar face tracking, B-roll, TTS ou MusicGen;
- não prometer tempo de processamento.

## Próximo gate

Após o relatório da Fase 1, a equipe decide se autoriza a Fase 2 — ingestão e validação. O benchmark de transcrição pertence à preparação da Fase 3 e pode ser antecipado apenas como spike explicitamente aprovado, sem alterar o provider definitivo silenciosamente.
