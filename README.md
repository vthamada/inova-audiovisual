# Inova Diamantina — Pipeline Audiovisual Inteligente

Fundação local-first para transformar vídeos brutos em primeiras versões editadas e auditáveis. O projeto preserva falas reais, originais, direitos de imagem e aprovação humana.

## Status

Fase 1 — fundação técnica. Ainda não há ingestão, transcrição ou render institucional completos. Nenhum comando publica conteúdo.

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
```

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

Consulte `docs/architecture/` para o desenho e `docs/implementation/phase-1-plan.md` para o escopo desta fase.
