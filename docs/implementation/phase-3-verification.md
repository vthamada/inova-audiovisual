# Verificação da Fase 3

- Data: 2026-07-31
- Branch: `codex/fase-3-transcricao`
- Escopo: runtime local de transcrição, adapter offline, CLI, schemas e documentação.

## Resultado implementado

- `faster-whisper==1.2.1` fixado em `pyproject.toml` e nos lockfiles de Windows/Python 3.12;
- CI ajustado para instalar `requirements-dev.lock` antes do pacote editável sem
  resolver dependências novamente;
- adapter local com `local_files_only=true`, modelo em diretório regular, versão do
  runtime e revisão de modelo conferidas;
- comando `inova-av project transcribe` e saída estruturada;
- transcript pendente de revisão, com SHA-256, metadados de provider e auditoria;
- recusa de provider remoto, egress, symlink, origem/hash divergentes, transcrição
  existente, metadados divergentes e timecode além da duração validada;
- timestamps por palavra e VAD conservador de 2 segundos no adapter.

## Evidência estrutural e sintética

| Verificação | Resultado |
|---|---|
| `pytest` | 60 testes passaram |
| Ruff | nenhum achado em repositório |
| mypy | sem erros em 27 arquivos-fonte |
| `pip check` | nenhuma dependência quebrada |
| adapter | double de `WhisperModel` confirma caminho local, `local_files_only`, VAD e timestamps |
| caso de uso | projeto sintético avança de `validated` para `transcribed` e cria auditoria |
| gate de modelo | CLI devolve código 2 com `model_revision: null`, antes de abrir mídia |
| HyperFrames doctor | Node 24, FFmpeg, FFprobe e Chrome encontrados; HyperFrames 0.7.82 permanece fixado, embora 0.7.86 esteja disponível; whisper-cpp, TTS, BGM e Docker ativo seguem opcionais/ausentes |

Nenhuma mídia institucional, áudio, transcript real ou peso de modelo foi incluído no Git
ou processado durante esta verificação.

## Não comprovado

Esta entrega não comprova qualidade de transcrição, execução com pesos locais, desempenho,
consumo de memória, aderência pt-BR ou comportamento com silêncio em mídia real. Essas
propriedades exigem o provisionamento autorizado e o benchmark definido no ADR-0002.
