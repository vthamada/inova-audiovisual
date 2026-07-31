# Ambiente atual

## Objetivo e data do diagnóstico

Este documento registra o estado observado em 29 de julho de 2026 para a Fase 0. Os resultados descrevem esta máquina e este checkout; não são promessa de desempenho do pipeline.

## Repositório

| Item | Resultado observado |
|---|---|
| Raiz confirmada | `D:\Users\DTI\Desktop\inova-audiovisual` |
| Evidência de repositório | Diretório `.git` na raiz; nenhum `.git` aninhado |
| Remoto `origin` | `https://github.com/vthamada/inova-audiovisual.git` |
| Referências remotas | `git ls-remote origin` retornou vazio |
| Branch inicial | `main`, ainda sem commits |
| Branch da Fase 0 | `codex/fase-0-arquitetura` |
| Estado inicial | Limpo, sem arquivos rastreados ou não rastreados |
| Histórico | Nenhum commit local ou remoto |
| Arquivos encontrados | Somente `.git` |
| Instruções locais | Não havia `AGENTS.md`, `README.md`, `DESIGN.md`, `SECURITY.md` ou outro documento |

A branch documental foi criada antes dos arquivos da Fase 0. Não foi executado `git init`, não foi criado repositório aninhado e nada foi movido para o repositório do portal.

## Sistema e hardware

| Componente | Resultado |
|---|---|
| Sistema | Microsoft Windows 11 Pro, 64 bits, versão `10.0.26200`, build `26200` |
| Shell | Windows PowerShell `5.1.26100.8894` |
| Equipamento | Dell OptiPlex 5070 |
| CPU | Intel Core i7-9700, 8 núcleos e 8 processadores lógicos, 3,0 GHz |
| GPU | Intel UHD Graphics 630 integrada, driver `31.0.101.2141`, memória reportada de 1 GiB |
| CUDA | Indisponível; PyTorch reportou zero dispositivos CUDA |
| Memória | 31,8 GiB totais; 12,5 GiB disponíveis no momento do `hyperframes doctor` |
| Disco do projeto (`D:`) | 755,9 GiB livres |
| Disco do cache temporário (`C:`) | Aproximadamente 208,8 GiB livres |

### Avaliação de capacidade

A máquina tem CPU, RAM e disco suficientes para desenvolver e validar o MVP local com vídeos curtos de uma pessoa, proxies e transcrição em CPU. Ela não tem GPU discreta para acelerar modelos CUDA. Renderização e transcrição devem começar com concorrência conservadora e ser medidas com material real. Modelos grandes, múltiplos workers de Chrome e processamento simultâneo podem pressionar a memória disponível.

## Ferramentas

| Ferramenta | Estado observado | Avaliação |
|---|---|---|
| Git | `2.47.1.windows.2` | Operacional |
| Node.js | `25.9.0` | Aceito pelo HyperFrames, porém a linha 25 está EOL; não usar como versão fixada do projeto |
| npm | `11.13.0` | Operacional; `npx.ps1` é bloqueado pela política do PowerShell, portanto usar `npx.cmd` |
| Python | `3.14.0`, única versão registrada pelo launcher | Operacional, mas não deve ser presumido compatível com todo o ecossistema de mídia/ML |
| FFmpeg | `N-123158-gcef2fbfd4b-20260304` em `C:\ffmpeg\bin` | Operacional; é snapshot de desenvolvimento e precisa ser fixado |
| FFprobe | Mesma build do FFmpeg | Operacional |
| Chrome | `150.0.7871.187` | Instalado, mas não substitui o Chrome Headless Shell exigido pelo HyperFrames |
| Edge | `150.0.4078.105` | Instalado; não foi validado como runtime de render |
| Docker | `29.2.0`, daemon em execução | Disponível para renders reproduzíveis e CI local |
| HyperFrames | `0.7.82`, executável sob demanda via `npx.cmd` | Diagnóstico funciona; render local ainda bloqueado por ausência do Chrome Headless Shell |

O `PATH` contém duas instalações de FFmpeg: `C:\ffmpeg\bin` e uma build `8.0.1` instalada pelo WinGet. A primeira prevalece. Essa ambiguidade pode produzir resultados diferentes entre terminais e deve ser eliminada na Fase 1 com resolução explícita, validação de versão e registro no manifesto.

Segundo a matriz oficial de releases do Node.js, a linha 25 já está EOL e a linha 24 é LTS. Referência: <https://nodejs.org/en/about/previous-releases>.

## Capacidades de mídia verificadas

Foram confirmados:

- codificação H.264 por `libx264`;
- codificação H.264 por Intel Quick Sync (`h264_qsv`) em um vídeo sintético de um segundo;
- presença de `libx265`, `hevc_qsv`, AAC, Opus e ProRes;
- filtros `silencedetect`, `loudnorm`, `ass`, `subtitles`, `cropdetect`, `drawtext` e `scale_qsv`;
- suporte a `libass`, FreeType e HarfBuzz na build ativa.

O teste curto confirma disponibilidade básica do encoder, não estabilidade, qualidade, velocidade ou compatibilidade com todos os arquivos de origem. Isso requer golden fixtures e benchmarks.

## Transcrição local

Estado observado:

- `openai-whisper==20250625`;
- `torch==2.10.0+cpu`;
- modelo multilíngue `medium.pt` já presente no cache, com aproximadamente 1,42 GiB;
- importação de `torch` e `whisper` bem-sucedida;
- MKL-DNN disponível;
- ajuda do CLI funciona quando `PYTHONUTF8=1`; sem UTF-8, o PowerShell em CP1252 gerou `UnicodeEncodeError`;
- nenhum teste de transcrição ponta a ponta ou benchmark foi executado;
- `whisper.cpp` não está instalado;
- `faster-whisper==1.2.1`, CTranslate2, PyAV e dependências foram instalados na
  `.venv` do projeto em 2026-07-31, sem pesos de modelo;
- o modelo baseline ainda não está provisionado e `model_revision` permanece nula,
  portanto qualquer tentativa operacional de transcrição falha antes de abrir mídia.

A instalação existente demonstra viabilidade técnica, mas não substitui o benchmark de
aceitação. O repositório usa ambiente isolado e versões fixadas; o provider recomendado e
o benchmark estão em `ADR-0002-transcription-provider.md`.

## HyperFrames

O comando `npx.cmd -y hyperframes@0.7.82 doctor` confirmou Node, CPU, memória, disco, FFmpeg, FFprobe e Docker. Identificou como ausentes:

- Chrome Headless Shell exigido para render local;
- `whisper-cpp` opcional;
- Kokoro TTS opcional;
- MusicGen opcional.

TTS e geração de música estão fora do MVP. O browser específico deve ser provisionado de forma versionada na Fase 1. A telemetria anônima informada pelo CLI deverá ser desabilitada antes do uso com materiais institucionais, e essa configuração deverá ser documentada.

Referências oficiais: <https://hyperframes.video/docs/getting-started/install> e <https://hyperframes.video/docs/workflow/cli-reference>.

## Limitações deste diagnóstico

- Não havia vídeo real, logo não foram medidos velocidade de transcrição, precisão em pt-BR, qualidade do áudio, detecção de rosto ou render 1080 × 1920.
- Não foi baixado o Chrome Headless Shell.
- Não foi validada aceleração Quick Sync com conteúdo real.
- Não foram medidos consumo de disco por minuto de vídeo nem duração de render.
- Não foram inspecionados logos, fontes, trilhas ou suas licenças, pois não há assets no repositório.
- O comando do Git mostrou aviso de acesso ao arquivo global de ignore sob o sandbox; isso não impediu as inspeções nem a criação autorizada da branch, mas deve ser reavaliado em execução comum.

## Comandos relevantes executados

```powershell
git status -sb
git remote -v
git branch --show-current
git log --oneline --decorate -10
git ls-remote origin
Get-ComputerInfo
Get-CimInstance Win32_Processor
Get-CimInstance Win32_VideoController
Get-CimInstance Win32_ComputerSystem
Get-CimInstance Win32_OperatingSystem
Get-PSDrive -PSProvider FileSystem
git --version
node --version
npm --version
python --version
py -0p
ffmpeg -hide_banner -version
ffprobe -hide_banner -version
ffmpeg -hide_banner -encoders
ffmpeg -hide_banner -filters
whisper --help
python -c "import torch, whisper; ..."
npx.cmd -y hyperframes@0.7.82 doctor
git switch -c codex/fase-0-arquitetura
```
