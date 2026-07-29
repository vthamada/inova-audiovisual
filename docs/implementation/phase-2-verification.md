# Verificação da Fase 2

- Data: 2026-07-29
- Branch: `codex/fase-2-ingestao`
- Resultado local: aprovado
- CI remoto: pendente do commit e push desta branch

## Resultado implementado

- comando `project ingest` com autorização nominal obrigatória;
- confinamento do projeto ao workspace e rejeição de symlinks;
- limites configuráveis de extensão, tamanho e espaço livre;
- cópia exclusiva em streaming, SHA-256 e verificação contra alteração concorrente;
- original interno somente leitura e sem sobrescrita de destinos;
- FFprobe e FFmpeg invocados por lista de argumentos, sem shell;
- validação obrigatória de vídeo, áudio, duração, dimensões e frame rate;
- proxy MP4 H.264/AAC, limitado a 1280x720 e sem upscale;
- relatórios e manifesto validados por JSON Schema;
- promoção de artefatos por staging e atualização atômica do projeto;
- quarentena rastreável e auditoria append-only;
- nenhum retry automático depois de uma escrita de resultado incerto.

## Evidência executada

| Comando ou verificação | Resultado |
|---|---|
| `scripts/verify.cmd` | aprovado |
| `python -m pytest` | 52 testes passaram em 1,84 s |
| `python -m ruff check .` | sem achados |
| `python -m mypy` | sem achados em 25 arquivos-fonte |
| `python -m pip check` | nenhuma dependência quebrada |
| schemas de projeto, probe e manifesto | aprovados |
| integração real FFmpeg/FFprobe | vídeo sintético com imagem e áudio aprovado |
| HyperFrames `doctor` | Node, FFmpeg, FFprobe e Chrome detectados |

O teste manual ponta a ponta usou apenas mídia sintética de um segundo. A ingestão
produziu o run `INGEST-20260729T192819685145Z-98774a46`, preservou hashes idênticos
entre origem e cópia, marcou a cópia como somente leitura, gerou proxy e registrou um
evento de auditoria. Um segundo exercício com extensão `.txt` retornou código `2`,
estado `quarantined` e manifesto válido.

## Cobertura relevante

- sucesso completo com doubles controlados;
- extensão inválida;
- falha de proxy;
- colisão sem sobrescrita;
- tentativa de projeto fora do workspace;
- mídia sintética real com verificação de dimensões, áudio e duração;
- schemas rejeitando path absoluto, frame rate zero e manifesto incompleto;
- regressão integral das regras de aprovação, estado, path, hash e auditoria da Fase 1.

## Limitações e pendências

- nenhuma mídia institucional real foi processada;
- não foi feito benchmark com arquivos longos, 4K/8K, VFR ou codecs de câmera;
- não existe recuperação automática de projeto quarentenado;
- Docker permanece opcional e o daemon não estava em execução;
- Whisper, Kokoro e MusicGen permanecem opcionais/fora desta fase;
- transcrição, edição, render e publicação continuam bloqueados por escopo e gates;
- a composição institucional ainda depende dos assets, fontes e aprovações visuais pendentes;
- o CI remoto desta branch deve ser confirmado após o push.

## Veredito

A Fase 2 atende localmente ao contrato de ingestão segura definido no arquivo de
contexto. Ela pode seguir para commit, push e CI remoto. O uso com mídia real deve
começar por um piloto autorizado e não substitui os benchmarks de formatos de câmera.
