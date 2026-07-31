# Provisionamento local de transcrição

## Estado atual

O runtime Python está fixado em `faster-whisper==1.2.1` para Windows x64. A distribuição
declara licença MIT; a licença específica de cada peso de modelo continua sendo um gate
separado. Nenhum peso de modelo foi baixado, convertido ou colocado neste repositório. O
diretório `models/` é ignorado pelo Git.

O adapter somente aceita um diretório local regular e sempre inicializa o runtime com
`local_files_only=true`. Se o modelo estiver ausente, o comando falha sem buscar um
fallback remoto.

## Gate antes de obter pesos

Uma pessoa responsável deve autorizar separadamente:

1. a origem do modelo e sua licença;
2. a versão/revisão exata;
3. o diretório local fora do Git;
4. a retenção e o controle de acesso do cache;
5. as três amostras de benchmark autorizadas descritas no
   [ADR-0002](../decisions/ADR-0002-transcription-provider.md).

Registre no controle institucional a origem, a licença, a revisão, o SHA-256 do pacote
ou diretório provisionado, a data e o responsável. Não registre segredos de Hub, tokens
ou qualquer mídia nesse controle versionado.

## Configuração após o provisionamento

O modelo baseline deve ficar em `models/faster-whisper/small/`.

Após verificar o diretório, substitua `model_revision: null` em
`config/pipeline.yaml` pela revisão efetivamente provisionada. Não altere
`provider_version`, `device`, `compute_type`, idioma, VAD ou `local_files_only` para
contornar a validação.

## Operação autorizada

Somente após a ingestão segura e autorização nominal da mídia:

    .\.venv\Scripts\inova-av.exe project transcribe workspace\<projeto> --actor "Nome do operador"

O projeto precisa estar em `validated`. O comando confere o SHA-256 da cópia interna,
o relatório técnico e os limites temporais antes de gravar
`02_processing/transcript.json`. A saída sempre começa com revisão pendente e nunca
autoriza edição, render ou publicação.

## Benchmark obrigatório

Compare o baseline `small` CPU/int8 com `openai-whisper medium` em pelo menos três
amostras autorizadas, total de 10–20 minutos. Registre tempo por minuto, pico de RAM,
qualidade de nomes e termos críticos, omissões, timestamps, silêncio e execução offline.
O benchmark é validação real separada; os testes do repositório não a substituem.
