# Preparação do ambiente

## Versões suportadas

- Python 3.12.10, instalado lado a lado;
- Node.js 24.18.0 LTS, preferencialmente isolado em `.tools` ou gerenciador equivalente;
- HyperFrames 0.7.82 como dependência npm local;
- FFmpeg/FFprobe validados pelo `doctor`;
- Chrome Headless Shell provisionado pelo HyperFrames.

As versões em `.python-version`, `.node-version`, `.nvmrc`, lockfiles e manifests são a fonte do projeto. O Node 25 do host não é suportado.

## Python

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
```

O `.venv` não entra no Git. Não instale dependências do projeto no Python global.

## Node e HyperFrames

Uma distribuição ZIP oficial do Node pode ser extraída em `.tools/node-v24.18.0-win-x64`. Essa pasta é ignorada. Com o runtime isolado:

```powershell
.\scripts\npm-project.cmd ci
.\scripts\npm-project.cmd run browser:ensure
```

Não use `npm.ps1`/`npx.ps1` neste host; a Execution Policy os bloqueia. O wrapper `scripts/npm-project.cmd` também garante que shims locais executem Node 24, e não o Node global.

Antes de material real, desabilite a telemetria do HyperFrames e confirme com o comando suportado pela versão fixada.

## FFmpeg

O host possui duas builds. `config/pipeline.yaml` deverá apontar para a build aprovada quando essa decisão for concluída. O `doctor` registra o executável resolvido e a versão.

Smoke tests sintéticos não autorizam uso com acervo real. A Fase 2 definirá fixtures e critérios de codecs.

## Diagnóstico

```powershell
.\scripts\doctor.cmd
.\scripts\doctor.cmd --json
```

O comando é somente leitura. Código de saída `0` indica que todos os requisitos da fundação foram localizados; `3` indica dependência obrigatória ausente ou incompatível.

## Offline

Depois que wheels, pacotes npm, browser e futuros modelos estiverem provisionados, o pipeline deverá funcionar com `network_policy: deny_by_default`. A Fase 1 não instala modelo de transcrição nem processa mídia.
