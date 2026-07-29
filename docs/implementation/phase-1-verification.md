# Verificação da Fase 1

- Data: 2026-07-29
- Branch: `codex/fase-1-fundacao`
- Resultado local: aprovado
- Commit: `36887feacb0660eba71ec05e63f6ea66e423c921`
- CI remoto: aprovado no GitHub Actions, execução `30483383949`

## Resultado implementado

- estrutura de repositório e políticas locais;
- Python 3.12.10 em `.venv` com locks separados de produção e desenvolvimento;
- Node 24.18.0 portátil com SHA-256 conferido contra `SHASUMS256.txt` oficial;
- HyperFrames 0.7.82 como dependência local e `package-lock.json`;
- Chrome Headless Shell 152.0.7928.2 no cache gerenciado pelo HyperFrames;
- telemetria do HyperFrames desabilitada;
- FFmpeg/FFprobe resolvidos explicitamente em `C:/ffmpeg/bin` e build esperada fixada;
- configuração `deny_by_default` validada por schema;
- CLI `inova-av` de versão, doctor, config e validação;
- dez schemas JSON 2020-12;
- máquina de estados e timecodes com aritmética decimal/racional;
- paths confinados à raiz;
- hashes canônicos e gate final sem bypass;
- logs humanos/JSON com redaction;
- eventos de auditoria JSONL append-only;
- portas para storage, transcrição, editorial e render;
- CI declarada para Windows e Linux, sem baixar browser ou modelo nos testes unitários.

## Evidência executada

| Comando ou verificação | Resultado |
|---|---|
| `scripts/verify.cmd` | passagem integrada concluída localmente |
| `python -m pytest` | 44 testes passaram |
| `python -m ruff check .` | sem achados |
| `python -m mypy` | sem achados em 21 arquivos-fonte |
| `python -m pip check` | nenhuma dependência quebrada |
| `inova-av --version` | `0.1.0` |
| `inova-av doctor` | todos os requisitos internos obrigatórios passaram |
| validação de config, projeto e assets | passou |
| HyperFrames `doctor` | Node 24, FFmpeg, FFprobe e Chrome detectados |
| instalação npm | 135 pacotes, zero vulnerabilidades reportadas no momento da instalação |
| `npm ci --ignore-scripts --dry-run` | lockfile consistente |
| segundo venv criado do `requirements-dev.lock` | instalação, 44 testes e `pip check` passaram |
| H.264 sintético por `libx264` e `h264_qsv` | passou no diagnóstico da Fase 0 |
| `.gitignore` para `.env`, `.venv`, `.tools`, `node_modules` e `workspace` | confirmado por `git check-ignore` |
| GitHub Actions `30483383949` | Windows, Linux e contrato Node passaram |

Os testes cobrem, entre outros:

- proibição de salto de draft para publicação;
- estado de quarentena;
- timecodes inválidos e fronteiras de frame;
- paths Windows/POSIX fora da raiz;
- schema e semântica de projeto, transcript, edit plan e manifestos;
- diretório contendo espaços;
- aprovação humana, revisão jurídica e autorização de imagem;
- invalidação após mudança de um byte no preview;
- artifact ausente;
- redaction de chaves e Bearer tokens;
- auditoria append-only.

## Mudanças fora do repositório

- Python 3.12.10 foi instalado lado a lado no escopo do usuário;
- Node portátil foi baixado em `.tools`, ignorado pelo Git;
- dependências Python estão em `.venv`, ignorado;
- dependências npm estão em `node_modules`, ignorado;
- Chrome Headless Shell foi salvo em `C:\Users\DTI\.cache\hyperframes\chrome`;
- a preferência de telemetria do HyperFrames foi registrada como desabilitada.

Nenhuma instalação Python ou npm do projeto foi feita globalmente. A instalação Python 3.14 e o Node 25 existentes não foram removidos.

## Limitações e pendências

- Docker está instalado, mas o daemon não estava em execução na última verificação; Docker é opcional para o modo interativo inicial.
- `whisper-cpp`, Kokoro e MusicGen permanecem ausentes; são opcionais ou fora do MVP.
- `faster-whisper` não foi instalado nem benchmarkado, conforme o limite da Fase 1.
- não existe composição HyperFrames: a assinatura canônica `Ecossistema de Inovação` e o logo horizontal autorizado foram registrados, mas o gate permanece bloqueado aguardando tipografia, demais assets oficiais, licenças e aprovação dos padrões audiovisuais.
- nenhum vídeo, modelo de transcrição ou dado pessoal foi processado.
- o snapshot FFmpeg foi fixado como baseline local da fundação e revalidado no início da Fase 2; sua distribuição ainda deve ser revista antes de empacotamento para outras máquinas.
- uma auditoria npm avulsa não foi enviada porque o egress de metadados do projeto não foi autorizado; a instalação npm autorizada reportou zero vulnerabilidades.
- a instalação limpa em outra máquina e o handoff por outra pessoa ainda não foram demonstrados.

## Veredito

A implementação satisfaz o escopo técnico da Fase 1 e foi aprovada localmente e no CI remoto. A validação humana do handoff em outra máquina permanece como pendência operacional, sem bloquear o início controlado da Fase 2.
