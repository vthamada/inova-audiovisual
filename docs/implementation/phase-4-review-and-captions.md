# Fase 4 — revisão de transcript e legendas

## Entrega

- revisão humana aceita somente para projeto em `transcribed`;
- o rascunho ASR em `02_processing/transcript.json` nunca é substituído;
- a versão revisada é gravada em `03_review/transcript.v<N>.json`;
- projeto e transcript precisam ter ID, SHA-256 de origem e versão coerentes;
- revisor, data e status `reviewed` são obrigatórios;
- o comando `project review-transcript --confirm-unchanged` registra uma aprovação humana
  somente quando o revisor declara que o rascunho foi comparado com a mídia e não exige texto alterado;
- a governança do projeto é marcada como transcript revisado sem avançar o estado editorial;
- evento append-only registra hashes do rascunho e da versão revisada;
- SRT e VTT são derivados determinísticos dos segmentos revisados, com no máximo duas linhas
  por cue e sem reescrever a fala.

## Evidência

Os testes sintéticos cobrem a aceitação de revisão, preservação do rascunho, auditoria,
revisor incompatível, quebra de linhas, ordem textual, distribuição de timecodes e os
serializadores SRT/VTT.

## Limites

Esta fase não cria revisão em nome de pessoa, não altera mídia, não produz ASS estilizado,
não faz análise editorial, não gera edit plan e não cria render. A revisão real exige
comparação humana com a mídia autorizada; a aprovação de identidade visual continua
bloqueada pelo checklist de DESIGN.md.
