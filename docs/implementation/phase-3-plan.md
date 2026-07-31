# Plano de implementação — Fase 3

**Status:** adapter local e comando implementados; pesos, benchmark e validação com mídia
autorizada permanecem pendentes.

## Objetivo

Criar a primeira transcrição rastreável de um projeto já validado, sem enviar mídia a
serviços externos e sem tratar a saída automática como conteúdo aprovado.

## Entrega atual

- contrato tipado de `TranscriptionProvider`, request, output e identidade do provider;
- configuração local-only derivada de `config/pipeline.yaml`;
- caso de uso `transcribe_project` para projeto em `validated`;
- conferência do SHA-256 da origem imutável antes de chamar o provider;
- recusa de provider remoto, provider/configuração divergentes, origem ambígua, symlink e
  sobrescrita de `transcript.json`;
- transcript JSON Schema 1.0 com `review.status=pending`, idioma canônico `pt-BR`,
  metadados de modelo e timecodes;
- validação semântica de segmentos e palavras: intervalos positivos, ordem monótona,
  ausência de sobreposição e palavras dentro do segmento;
- escrita atômica, SHA-256 do transcript, transição `validated -> transcribed` e evento
  de auditoria `transcription_completed`.

O provider é injetado no caso de uso e o adapter `faster-whisper 1.2.1` é carregado
somente quando chamado. Isso permite testar o fluxo sem baixar pesos ou processar mídia
institucional.

## Fora do escopo desta entrega

- baixar, converter ou armazenar pesos de modelo;
- extrair WAV ou processar mídia real;
- revisão humana, correção, SRT/VTT/ASS, diarização e análise editorial.

## Próximo gate

Antes da primeira transcrição real, a equipe deve autorizar o provisionamento local e
selecionar pelo menos três amostras autorizadas (10–20 minutos no total) para o benchmark definido no
[ADR-0002](../decisions/ADR-0002-transcription-provider.md). O modelo e o cache devem
ficar fora do Git; a execução deve continuar com `local_files_only=true` e sem fallback
remoto.

## Evidência necessária para concluir a Fase 3

1. testes sintéticos do caso de uso, schema e auditoria;
2. `pytest`, Ruff, mypy e `pip check` verdes;
3. provisionamento com revisão, origem, checksum e licença do modelo registrados;
4. benchmark offline autorizado contra `openai-whisper medium`;
5. revisão humana de transcrições, nomes, cargos, datas e instituições.
