# Plano de implementação — Fase 2

**Status:** implementado e aprovado localmente e no CI remoto em 2026-07-29 na branch `codex/fase-2-ingestao`.

## Objetivo

Receber um arquivo de vídeo local autorizado, preservá-lo por cópia verificada, validar sua estrutura com FFprobe, gerar um proxy de trabalho e avançar o projeto de `received` para `validated`. Qualquer falha técnica deve produzir quarentena rastreável, sem sobrescrever arquivos existentes e sem sucesso falso.

## Escopo

Incluído:

- comando `inova-av project ingest` com confirmação nominal de autorização;
- confinamento do projeto ao `workspace_root` configurado;
- rejeição de symlinks, extensões não permitidas, arquivo vazio e tamanho excessivo;
- cópia com criação exclusiva, SHA-256 durante o streaming e comparação de metadados antes/depois;
- nome interno independente do nome não confiável recebido;
- FFprobe por argumentos, sem shell;
- relatório técnico validado por JSON Schema;
- proxy H.264/AAC em MP4, sem upscale, validado novamente por FFprobe;
- manifesto de ingestão, hashes de artefatos e versões das ferramentas;
- atualização atômica de `project.yaml`;
- auditoria append-only;
- quarentena com estágio e motivo acionável;
- testes com mídia sintética; nenhuma mídia institucional real.

Fora do escopo:

- transcrição, extração WAV e diarização;
- análise editorial, cortes e legendas;
- composições HyperFrames e renders institucionais;
- publicação;
- ingestão em lote, rede, Drive ou SaaS;
- recuperação automática de um projeto já quarentenado.

## Contrato do comando

```powershell
inova-av project ingest <diretorio-do-projeto> <arquivo-local> --authorized-by "Nome"
```

O projeto deve começar em `received`. A saída estruturada opcional é habilitada por `--json`. O comando retorna:

- `0`: ingestão validada;
- `2`: entrada inválida ou mídia enviada à quarentena;
- `3`: FFmpeg/FFprobe ausente ou incompatível.

## Artefatos

Sucesso:

```text
<projeto>/
  project.yaml
  audit.jsonl
  01_inbox/source-<sha12>.<ext>
  02_processing/technical-report.json
  02_processing/proxy.mp4
  02_processing/proxy-technical-report.json
  02_processing/ingest-manifest.json
```

Falha validável:

```text
<projeto>/
  project.yaml
  audit.jsonl
  99_quarantine/<run-id>/
    ingest-manifest.json
    source.<ext>        # somente quando a cópia já havia sido criada
    ...                 # diagnóstico parcial disponível
```

## Invariantes

- o original externo nunca é alterado;
- nenhum destino existente é sobrescrito;
- o checksum registrado é o checksum da cópia efetivamente produzida;
- a cópia final fica sem permissão de escrita;
- paths persistidos são relativos ao projeto;
- comandos de mídia nunca usam `shell=True`;
- o projeto só chega a `validated` depois de original, probe e proxy válidos;
- qualquer falha antes do commit deixa o projeto em `quarantined` e preserva diagnóstico;
- nenhum retry automático ocorre quando o resultado de uma escrita é incerto.

## Evidência de conclusão

- testes unitários de sucesso, extensão inválida, falha de proxy, colisão e escape do workspace;
- integração real com vídeo sintético contendo vídeo e áudio;
- schemas do relatório técnico e manifesto;
- CLI exercitada em diretório com espaços;
- pytest, Ruff, mypy, `pip check` e `scripts/verify.cmd` verdes;
- revisão do diff e confirmação de que nenhuma fixture de mídia entrou no Git.
