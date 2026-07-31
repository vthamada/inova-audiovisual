# Proveniência do modelo `faster-whisper-small`

- Data de provisionamento: 2026-07-31
- Responsável pela autorização: Ricardo Hamada
- Finalidade: transcrição local em pt-BR do pipeline audiovisual do Inova Diamantina
- Provider: `faster-whisper` 1.2.1 / CTranslate2
- Repositório de origem: `Systran/faster-whisper-small` no Hugging Face
- Revisão fixada: `536b0662742c02347bc0e980a01041f333bce120`
- Licença declarada pelo repositório: MIT
- Diretório local: `models/faster-whisper/small/` (ignorado pelo Git)
- Rede: download de pesos somente; não houve envio de vídeo, áudio, transcript ou metadados do projeto
- Credenciais: nenhuma; download anônimo, sem token

## Integridade após o download

| Arquivo | SHA-256 |
|---|---|
| `config.json` | `b55496ac7940a7ae47d2c01eab40edfd8701feec1229d9cce3b40014383fb828` |
| `model.bin` | `3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671` |
| `tokenizer.json` | `fb7b63191e9bb045082c79fd742a3106a12c99513ab30df4a0d47fa6cb6fd0ab` |
| `vocabulary.txt` | `34ce3fe1c5041027b3f8d42912270993f986dbc4bb34cf27f951e34a1e453913` |

O diretório contém 486.212.372 bytes. Seu hash de manifesto, calculado a partir de
`nome-do-arquivo:sha256` em ordem lexicográfica, é
`35ac7bd363f7ebda4adb6802d7b6f63ca185cb7b1fafe88d2c0934f83c7b12a3`.

## Limites operacionais

Depois do provisionamento, o adapter carrega apenas esse diretório e usa
`local_files_only: true`; a execução de transcrição não pode fazer fallback remoto.
Todo transcript permanece rascunho pendente de revisão humana. Nomes, cargos,
instituições e direitos de imagem/voz continuam sujeitos aos gates já definidos.
