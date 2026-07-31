# Proveniência do modelo `faster-whisper-large-v3`

- Data de provisionamento: 2026-07-31
- Responsável pela autorização: Ricardo Hamada
- Finalidade: benchmark e transcrição local em pt-BR do pipeline audiovisual do Inova Diamantina
- Provider: `faster-whisper` 1.2.1 / CTranslate2
- Repositório de origem: `Systran/faster-whisper-large-v3` no Hugging Face
- Revisão fixada: `edaa852ec7e145841d8ffdb056a99866b5f0a478`
- Licença declarada pelo repositório: MIT
- Diretório local: `models/faster-whisper/large-v3/` (ignorado pelo Git)
- Rede: download de pesos somente; não houve envio de vídeo, áudio, transcript ou metadados do projeto
- Credenciais: nenhuma; download anônimo, sem token

## Integridade após o download

| Arquivo | SHA-256 |
|---|---|
| `config.json` | `a9306624f5ec14270a014b647e5c316b6e03a662c369758d1b90697a7b0655b9` |
| `model.bin` | `69f74147e3334731bc3a76048724833325d2ec74642fb52620eda87352e3d4f1` |
| `preprocessor_config.json` | `7ccc62c6f2765af1f3b46c00c9b5894426835a05021c8b9c01eecb6dfb542711` |
| `tokenizer.json` | `6d8cbd7cd0d8d5815e478dac67b85a26bbe77c1f5e0c6d76d1ce2abc0e5f21ca` |
| `vocabulary.json` | `c69260f2ab26d659b7c398f9a2b2b48ed0df16c3b47d7326782fd9cba71690c1` |

O diretório contém 3.090.835.702 bytes. Seu hash de manifesto, calculado a partir de
`nome-do-arquivo:sha256` em ordem lexicográfica, é
`34fe9dbe32b318f6780ba0ab9caef8fc25f7c856b5dde854499c4f42fbc66ba6`.

## Uso permitido

O adapter carrega somente esse diretório e usa `local_files_only: true`. O modelo é um
candidato de maior fidelidade após a reprovação qualitativa do `small`; cada resultado
continua pendente de revisão humana e não autoriza edição, render ou publicação.
