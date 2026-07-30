# Avaliação de skills e motores de vídeo para Codex

- Data da avaliação: 2026-07-30
- Escopo: pipeline audiovisual local-first do Inova Diamantina
- Plataforma prioritária: Windows 11, PowerShell, Python 3.12 e Node 24 LTS
- Política de rede: `deny_by_default`
- Resultado: **HyperFrames é o único motor principal recomendado para composição e motion**

## Resumo executivo

O inventário encontrou HyperFrames ativo e fixado no projeto, uma skill oficial de
Remotion presente apenas no cache local e nenhuma instalação de VideoDB. A pesquisa
também confirmou uma skill pública oficial do VideoDB, mas ela opera sobre um serviço
server-side e requer API key, upload/processamento remoto e cobrança por créditos.
Nenhuma dependência, plugin ou skill foi instalada durante esta avaliação.

Recomenda-se manter:

1. **HyperFrames** como único motor principal de composição programática, templates e motion;
2. **FFmpeg/FFprobe** como camada técnica de mídia, corte, áudio, probe, codec e empacotamento;
3. skills próprias do Inova como camada de política, contratos e gates sobre essas ferramentas.

Não se recomenda instalar ou operar Remotion e VideoDB no baseline. Remotion duplicaria
o motor visual e acrescentaria React, bundler e uma licença especial. VideoDB resolveria
busca, percepção e edição server-side, mas entraria em conflito direto com a arquitetura
local-first e com a proibição de egress de mídia.

## Método e limites

Foram usados quatro tipos de evidência:

- inventário somente leitura das skills e plugins já presentes no ambiente;
- manifests, lockfiles e documentação do próprio repositório;
- documentação e repositórios oficiais dos fornecedores;
- verificação local sem rede do runtime já instalado.

Não foram executados:

- instalação, atualização ou ativação de skill;
- `npm install`, `pip install`, `npx skills add` ou equivalente;
- upload de mídia, chamada de API ou criação de conta;
- composição, preview ou render HyperFrames;
- teste Remotion ou VideoDB;
- processamento de material real.

Portanto, esta avaliação comprova arquitetura, contratos publicados e presença local;
não comprova qualidade visual com material institucional real.

## Inventário observado

| Item | Situação em 2026-07-30 | Evidência |
|---|---|---|
| HyperFrames | instalado localmente no projeto | `hyperframes@0.7.82`, Apache-2.0, Node `>=22` |
| Skill `hyperframes` | disponível e ativa no ambiente Codex | authoring HTML/CSS/GSAP e gates de composição |
| Skill `hyperframes-cli` | disponível e ativa | lint, validate, inspect, preview, render e doctor |
| Skill `gsap` | disponível como apoio ao HyperFrames | animação determinística e timelines |
| Skill `hyperframes-registry` | disponível, mas não autorizada para importar blocos | registry remoto opcional; nenhum bloco foi instalado |
| Remotion Agent Skills | somente cache local; não ativa no catálogo desta sessão | skill oficial de boas práticas em React/TSX |
| VideoDB Skills | não instalada | repositório público oficial encontrado na pesquisa |
| `.agents/skills` do Inova | implementado em 2026-07-30 | seis skills específicas, cada uma com `SKILL.md` e metadados de interface |

O runtime local verificado é Node `v24.18.0`, HyperFrames `0.7.82`, Chrome Headless
Shell `152.0.7928.2` e FFmpeg no caminho explícito `C:/ffmpeg/bin`. A release
HyperFrames `0.7.83` foi publicada em 2026-07-30, mas **não foi instalada**. O projeto
deve continuar fixado em `0.7.82` até benchmark e revisão de changelog.

## Separação de responsabilidades

O termo “motor de vídeo” mistura responsabilidades distintas. Para evitar dois núcleos
concorrentes, esta avaliação adota a seguinte taxonomia:

| Camada | Responsabilidade | Escolha |
|---|---|---|
| domínio e workflow | estados, contratos, auditoria, aprovação | Python do Inova |
| processamento de mídia | probe, cópia, áudio, cortes, codec, empacotamento | FFmpeg/FFprobe |
| composição e motion | layout, lower thirds, aberturas, encerramentos, overlays | **HyperFrames** |
| percepção/search remoto | indexação semântica, streaming e VLM server-side | não adotado |
| acabamento excepcional | intervenção manual em NLE | fora do motor principal |

FFmpeg é indispensável, mas é tratado como ferramenta de mídia de baixo nível. Assim,
“um único motor principal” significa um único framework de composição programática:
HyperFrames.

## Comparação detalhada

| Opção | Finalidade | Licença | Manutenção | Dependências e Windows | Execução e tráfego | Custos | Riscos e sobreposição | Adequação ao Inova |
|---|---|---|---|---|---|---|---|---|
| **HyperFrames** | HTML/CSS/GSAP para composição, preview, QA e render | Apache-2.0; uso local sem taxa por render | muito ativa, releases frequentes; ainda `0.x`, com risco de churn | Node 22+, FFmpeg e Chrome Headless; runtime e diagnóstico local demonstrados no Windows, mas render institucional ainda não validado | local após provisionamento; telemetria é desativável; URLs, fontes, registry e cloud podem gerar egress e devem ser bloqueados | sem licença/per-render local; custo de CPU, RAM, disco e eventual cloud opcional | browser aumenta peso; pixels podem variar com upgrades; registry/CDN podem introduzir supply-chain e rede | **alta**: já fixado, integrado ao ADR-0003 e orientado a agentes |
| **Remotion Agent Skills + Remotion** | React/TSX para vídeos programáticos, Studio, Player e render | skill oficial sem licença destacada no repositório consultado; runtime sob licença especial Remotion | madura, equipe dedicada e releases frequentes na linha 4.x | Node, React, bundler, browser e stack `@remotion/*`; documentação contém cuidados específicos para shell Windows | render local possível; Lambda/Cloud Run/Vercel são opcionais; assets e fontes externas podem gerar egress | elegibilidade gratuita depende da entidade; planos publicados incluem US$ 25/mês por creator e automação a US$ 0,01/render com mínimo de US$ 100/mês | duplica HyperFrames, cria dois DSLs, dois QA loops e dúvida de licença; migração sem benefício comprovado | média isoladamente, **baixa no projeto atual** |
| **VideoDB Skills** | ingestão, transcrição, VLM, busca, edição, geração e HLS server-side | código da skill MIT; serviço e dados sujeitos a termos comerciais separados | projeto oficial recente e ativo, mas menor e acoplado ao fornecedor | Python 3.9+ e SDK VideoDB; skill declara PowerShell/Windows | requer API key e chamadas a `api.videodb.io`; upload local envia a mídia e os derivados ficam acessíveis pelo serviço/HLS | créditos de entrada anunciados; custo varia por armazenamento, transcrição, indexação, frames e modelos; tabela unitária pública não foi confirmada | egress de mídia, segredo, residência/retenção não validadas, lock-in e custo variável; sobrepõe ingestão, transcrição e edição locais | **incompatível com o baseline** `deny_by_default` |
| **FFmpeg/FFprobe direto** | mídia, áudio, filtros, legendas e codecs via CLI | LGPL ou GPL conforme a configuração da build; deve ser verificada por distribuição | muito madura e ativa; release 8.1.2 publicada e FATE multiplataforma | binários Windows disponíveis por distribuidores indicados pelo projeto; build local já fixada | inteiramente local salvo protocolos/URLs explicitamente usados | sem taxa; custo computacional local | filtergraphs de motion são difíceis de manter; não oferece Studio nem inspeção visual equivalente | **essencial como camada técnica**, não escolhido como motor de motion |
| Skills gerais de produção/Figma motion | intake, storyboard, handoff ou design | varia por plugin/serviço | varia | normalmente browser, Figma ou ferramentas de design | pode exigir serviços externos | varia | não renderizam o master e não substituem contratos do pipeline | auxiliares somente mediante autorização específica |

### Licença não é apenas a licença da skill

Uma skill é um conjunto de instruções para o agente. Sua licença não concede
automaticamente direito sobre o runtime ou o serviço chamado:

- HyperFrames reúne skill e runtime no mesmo projeto Apache-2.0;
- Remotion Skills orienta o uso, mas o motor continua sujeito à licença Remotion;
- VideoDB Skills é MIT, mas a API, armazenamento e modelos continuam sendo um serviço;
- a licença efetiva do FFmpeg depende dos componentes habilitados na build distribuída.

Antes de qualquer produção comercial ou contratação, a entidade jurídica do Inova e a
build FFmpeg devem passar por validação administrativa/jurídica própria.

## Matriz de decisão

Escala: 1 = fraco, 3 = aceitável, 5 = forte. A nota mede adequação ao projeto atual,
não qualidade universal do produto.

| Critério | Peso | HyperFrames | Remotion | VideoDB | FFmpeg direto |
|---|---:|---:|---:|---:|---:|
| local-first e governança de dados | 25% | 5 | 5 | 1 | 5 |
| compatibilidade com arquitetura existente | 20% | 5 | 2 | 1 | 5 |
| adequação a Codex/agent authoring | 15% | 5 | 4 | 4 | 2 |
| QA visual e experiência de composição | 10% | 5 | 3 | 2 | 1 |
| Windows | 10% | 4 | 4 | 4 no cliente | 5 |
| previsibilidade de licença e custo | 10% | 5 | 2 | 1 | 4 |
| maturidade e manutenção | 10% | 3 | 5 | 3 | 5 |
| **nota ponderada** | **100%** | **4,70** | **3,65** | **2,05** | **4,05** |

FFmpeg pontua bem porque é excelente na própria camada, mas não resolve a experiência
de motion e QA visual. HyperFrames é o único candidato que combina a nota mais alta com
a função exata de motor principal de composição.

## Decisão e controles para HyperFrames

Adotar HyperFrames como único motor principal, com estes controles obrigatórios:

1. manter versão exata no `package-lock.json`;
2. não atualizar de `0.7.82` sem changelog, teste sintético e benchmark Windows;
3. manter telemetria desabilitada e `HYPERFRAMES_NO_TELEMETRY=1` no worker futuro;
4. proibir URLs remotas, CDN, Google Fonts e assets fora do registry aprovado;
5. não usar `hyperframes add` sem revisão de origem, licença, arquivos e hashes;
6. executar `lint`, `validate` e `inspect` antes de preview/render;
7. validar outputs com FFprobe e registrar versões e hashes;
8. não criar composição enquanto o status de `DESIGN.md` continuar pendente;
9. não emitir render final sem `approval.json` íntegro;
10. limitar workers e medir CPU, RAM, disco e tempo no piloto autorizado.

Remotion permanece somente como alternativa de contingência estudada. Sua adoção
exigiria benchmark comparativo, parecer de licença, plano de migração e novo ADR. Não
se deve manter os dois frameworks no mesmo pipeline.

VideoDB permanece fora do baseline. Um experimento futuro exigiria autorização de
egress específica, DPA/termos, residência e retenção de dados, orçamento, mídia
sintética ou não sensível e um provider explicitamente remoto. O modo local nunca deve
degradar silenciosamente para VideoDB.

## Skills específicas implementadas em `.agents/skills`

As skills do Inova contêm política e workflow próprios, sem copiar a documentação
inteira de HyperFrames, FFmpeg ou Whisper. A ordem implementada é:

### 1. `inova-audiovisual-governance`

- **Disparo:** qualquer trabalho com mídia, transcript, assets, render ou publicação.
- **Função:** verificar autorização, `network_policy`, imutabilidade, SHA-256, direitos
  de imagem, registro de assets, redaction, estado e escopo autorizado.
- **Bloqueios:** mídia real sem autorização, serviço externo, segredo no Git, alteração
  de original, bypass de aprovação ou publicação implícita.
- **Referências:** `AGENTS.md`, `SECURITY.md`, `docs/architecture/security-and-governance.md`.

### 2. `inova-ingest-and-probe`

- **Disparo:** receber, copiar, validar, criar proxy ou quarentenar mídia.
- **Função:** operar o comando existente de ingestão, conferir FFmpeg/FFprobe explícitos,
  hashes, reports, manifestos e quarentena.
- **Não faz:** transcrição, edição ou render.
- **Referências:** schemas de project, media-probe e ingest-manifest, além da verificação da Fase 2.

### 3. `inova-transcription-ptbr`

- **Disparo:** extração de áudio, ASR pt-BR, SRT/VTT ou revisão de transcript.
- **Função:** exigir provider local, `local_files_only`, timestamps monotônicos,
  confiança, trechos inaudíveis explícitos e revisão humana.
- **Bloqueios:** completar fala por inferência, tratar transcript automático como fato
  aprovado ou enviar áudio a API.
- **Referências:** ADR-0002, transcript schema e regras editoriais de fidelidade.

### 4. `inova-editorial-edit-plan`

- **Disparo:** seleção de trechos, roteiro, análise e plano de corte.
- **Função:** separar fala literal de texto editorial, manter arquivo/in/out, justificar
  cada corte e produzir somente `edit-plan` validável.
- **Bloqueios:** alterar sentido, fabricar citação, decidir publicação ou render final.
- **Referências:** data flow, edit-plan schema e máquina de estados.

### 5. `inova-hyperframes-brand-motion`

- **Disparo:** hero frame, lower third, abertura, encerramento, overlay ou composição.
- **Pré-condição dura:** `DESIGN.md` aprovado, assets registrados, fontes licenciadas,
  áreas seguras e tokens de motion aprovados.
- **Função:** aplicar assinatura “Ecossistema de Inovação”, contratos HyperFrames,
  layouts 16:9/9:16/1:1, GSAP determinístico e componentes institucionais.
- **Bloqueios:** “Pacto pela Inovação” como assinatura permanente, CDN, asset genérico,
  pessoa gerada por IA, `Math.random`, tempo de parede ou registry não revisado.
- **Referências:** skill upstream `hyperframes`, `DESIGN.md`, visual audit e assets registry.

### 6. `inova-render-verification`

- **Disparo:** preview, draft, render candidate, aprovação ou handoff.
- **Função:** executar lint/validate/inspect, snapshots/golden frames, FFprobe, loudness,
  hashes, manifestos e checks de acessibilidade; distinguir evidência estrutural,
  smoke sintético e validação real autorizada.
- **Bloqueios:** chamar draft de final, aceitar warning material sem decisão, render final
  sem `approval.json` correspondente ou publicar.
- **Referências:** ADR-0003, ADR-0004, render schemas e runbooks.

### Estrutura implementada

```text
.agents/skills/
  inova-audiovisual-governance/
    SKILL.md
  inova-ingest-and-probe/
    SKILL.md
  inova-transcription-ptbr/
    SKILL.md
  inova-editorial-edit-plan/
    SKILL.md
  inova-hyperframes-brand-motion/
    SKILL.md
  inova-render-verification/
    SKILL.md
```

Cada skill é pequena, tem frontmatter `name`/`description`, declara entradas, saídas,
ações proibidas e critérios de conclusão. Elas foram criadas em 2026-07-30 sem scripts
duplicados: os workflows chamam os CLIs e contratos do repositório em vez de
reimplementar regras.

## Fontes oficiais consultadas

### HyperFrames

- [repositório, requisitos e licença](https://github.com/heygen-com/hyperframes)
- [licença Apache-2.0](https://github.com/heygen-com/hyperframes/blob/main/LICENSE)
- [releases](https://github.com/heygen-com/hyperframes/releases)
- [CLI e telemetria](https://hyperframes.heygen.com/packages/cli)
- [comparação oficial HyperFrames/Remotion](https://github.com/heygen-com/hyperframes/blob/main/README.md#hyperframes-vs-remotion)

### Remotion

- [documentação e requisitos](https://www.remotion.dev/docs/)
- [render CLI](https://www.remotion.dev/docs/cli/render)
- [renderer server-side](https://www.remotion.dev/docs/renderer)
- [licença do runtime](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)
- [preços publicados](https://www.remotion.dev/)
- [Agent Skills oficiais](https://github.com/remotion-dev/skills)

### VideoDB

- [VideoDB Skills oficial](https://github.com/video-db/skills)
- [licença MIT da skill](https://github.com/video-db/skills/blob/main/LICENSE)
- [API e autenticação](https://docs.videodb.io/api-reference/introduction)
- [upload de arquivo local](https://docs.videodb.io/pages/ingest/files-and-collections/upload-video)
- [custos e latência de indexação](https://docs.videodb.io/pages/understand/quality-and-evaluation/latency-and-cost)
- [exclusão de coleção e derivados](https://docs.videodb.io/api-reference/collections/delete_collection)

### FFmpeg

- [downloads, release e builds Windows indicadas](https://ffmpeg.org/download.html)
- [plataformas suportadas](https://www.ffmpeg.org/platform.html)
- [repositório e arquivos de licença](https://github.com/FFmpeg/FFmpeg)
