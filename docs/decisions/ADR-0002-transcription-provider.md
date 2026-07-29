# ADR-0002 — Provider de transcrição

- Status: Aceito, condicionado a benchmark
- Data: 2026-07-29
- Decisores: equipe Inova Diamantina
- Aprovação: usuário, 2026-07-29

## Contexto

O MVP exige pt-BR, timestamps, funcionamento local e custo previsível. A máquina possui i7-9700, 32 GiB e somente GPU Intel integrada. `openai-whisper` com PyTorch CPU e modelo `medium` já existe no host, mas não houve benchmark. HyperFrames não encontrou `whisper-cpp`.

As opções principais são:

1. `faster-whisper`/CTranslate2;
2. `openai-whisper`/PyTorch;
3. `whisper.cpp`;
4. API externa, somente opt-in futuro.

## Decisão

Definir `TranscriptionProvider` independente e adotar `faster-whisper` como provider local preferencial, com:

- CPU;
- `compute_type=int8`;
- idioma explícito `pt`;
- word timestamps quando disponíveis;
- VAD conservador configurável;
- modelo `small` como baseline operacional;
- modelo `medium` como candidato de maior qualidade;
- cache de modelos fora do Git;
- modo `local_files_only` para execução offline após provisionamento.

A adoção se torna definitiva somente após benchmark contra o `openai-whisper medium` existente. Se `faster-whisper` falhar nos critérios, o adapter OpenAI Whisper será o fallback inicial. `whisper.cpp` permanece alternativa futura de empacotamento.

## Benchmark de aceitação

Usar pelo menos três amostras autorizadas, totalizando cerca de 10–20 minutos, contendo:

- fala clara;
- ruído e reverberação realistas;
- nomes próprios, instituições e termos territoriais;
- variação de ritmo.

Medir:

- tempo real por minuto;
- pico de RAM;
- erros em nomes/termos críticos;
- omissões e alucinações;
- qualidade dos timestamps;
- comportamento em silêncio;
- execução offline.

A escolha prioriza fidelidade e revisabilidade, não apenas velocidade. Resultados e versões serão registrados.

## Consequências

### Positivas

- CPU `int8` é compatível com a máquina;
- VAD e timestamps por palavra estão disponíveis;
- provider permanece substituível;
- nenhuma mídia precisa sair do computador.

### Negativas

- os pesos CTranslate2 não reutilizam diretamente o `medium.pt` atual;
- primeiro provisionamento exige download ou conversão controlada;
- CPU será mais lenta que GPU discreta;
- qualidade pt-BR precisa de validação humana;
- Python e wheels devem ser testados na versão fixada.

## Regras

- transcript automático nunca é fato aprovado;
- nomes, cargos, datas e instituições exigem revisão;
- saída deve preservar confiança e timecodes quando fornecidos;
- fala literal e texto corrigido permanecem separados;
- provider remoto não é fallback automático;
- toda execução registra modelo, revisão, compute type e hashes.

## Referências

- Faster Whisper: <https://github.com/SYSTRAN/faster-whisper>
- OpenAI Whisper: <https://github.com/openai/whisper>
- whisper.cpp: <https://github.com/ggml-org/whisper.cpp>
