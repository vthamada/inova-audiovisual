# ADR-0006 — baseline de fidelidade para transcrição

- Status: Aceito, condicionado a benchmark humano
- Data: 2026-07-31
- Decisor: Ricardo Hamada
- Substitui a escolha operacional de baseline da ADR-0002

## Contexto

O `faster-whisper small` passou nos testes estruturais e na execução local, mas os
rascunhos obtidos de vídeos reais autorizados do evento não corresponderam fielmente ao
áudio segundo a avaliação humana. Ele não pode ser promovido para legendas ou edição.

O `openai-whisper` é a implementação de referência, mas não está instalado nem verificado
no ambiente Python 3.12 do projeto. O `faster-whisper` já é o runtime local versionado,
executa a família Whisper por CTranslate2 e preserva o modo offline.

## Decisão

Adotar `faster-whisper large-v3` em CPU/int8 como candidato principal de fidelidade. Os
pesos vêm do repositório MIT `Systran/faster-whisper-large-v3`, em revisão imutável e
fora do Git. A configuração efetiva permanece com `local_files_only: true`.

Os rascunhos anteriores não são sobrescritos. Uma nova ingestão de benchmark usa projetos
distintos e mantém hashes, provider, revisão e auditoria separados.

## Consequências

- maior probabilidade de fidelidade em pt-BR que o modelo `small`;
- download aproximado de 3,1 GB e tempo maior em CPU;
- ainda exige comparação humana com fala clara, ruído e termos institucionais;
- `openai-whisper medium` permanece comparador futuro, não fallback automático;
- nenhum resultado de ASR é fato aprovado sem revisão humana.
