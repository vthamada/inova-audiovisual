# Inova Diamantina — Pipeline Audiovisual Inteligente

Fundação local-first para transformar vídeos brutos em primeiras versões editadas e auditáveis. O projeto preserva falas reais, originais, direitos de imagem e aprovação humana.

## Status

Fase 2 — ingestão local segura. O pipeline copia uma mídia autorizada sem alterar o
original, verifica o SHA-256, inspeciona vídeo e áudio com FFprobe, cria um proxy de
trabalho e envia falhas para quarentena rastreável. Transcrição, edição, render
institucional e publicação ainda não fazem parte desta entrega.

## Requisitos

- Windows 11 como plataforma prioritária;
- Python 3.12.10;
- Node.js 24.18.0 LTS;
- FFmpeg e FFprobe fixados conforme a política operacional;
- Chrome Headless Shell gerenciado pelo HyperFrames.

## Instalação de desenvolvimento

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
.\scripts\npm-project.cmd ci
.\scripts\npm-project.cmd run browser:ensure
```

Não use mídia real antes de concluir as configurações de privacidade, assets e telemetria.

## Comandos atuais

```powershell
.\.venv\Scripts\inova-av.exe --version
.\scripts\doctor.cmd
.\scripts\doctor.cmd --json
.\.venv\Scripts\inova-av.exe config show
.\.venv\Scripts\inova-av.exe schema validate project schemas\examples\project.valid.yaml
.\.venv\Scripts\inova-av.exe project validate schemas\examples\project-directory
.\.venv\Scripts\inova-av.exe project ingest workspace\meu-projeto C:\midias\video.mp4 --authorized-by "Nome do operador"
```

O diretório do projeto precisa estar dentro de `workspace/`, conter um `project.yaml`
válido e estar no estado `received`. Use `--json` para obter uma resposta estruturada.
O retorno é `0` para sucesso, `2` para quarentena/entrada inválida e `3` para
FFmpeg ou FFprobe ausente/incompatível.

## Verificação

```powershell
.\scripts\verify.cmd
```

## Gates

- originais nunca são alterados;
- rede é negada por padrão;
- assets sem origem e licença não entram em render;
- nenhuma composição é criada antes de `DESIGN.md` ser aprovado;
- render final exige aprovação humana ligada aos hashes dos artefatos;
- publicação permanece fora do MVP.

Consulte `docs/architecture/` para o desenho e
`docs/implementation/phase-2-verification.md` para o escopo e as evidências atuais.
