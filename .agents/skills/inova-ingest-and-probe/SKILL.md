---
name: inova-ingest-and-probe
description: Receber, copiar, inspecionar, criar proxy ou quarentenar mídia local no pipeline audiovisual do Inova Diamantina. Usar quando houver ingestão de arquivo autorizado, validação com FFprobe, geração de proxy, conferência de SHA-256, manifesto de ingestão ou diagnóstico de quarentena.
---

# Ingestão e Probe Inova

Usar `$inova-audiovisual-governance` antes desta skill. Operar somente pelo CLI e contratos existentes.

## Ler antes de agir

- `README.md`, seção de comandos atuais;
- `config/pipeline.yaml`;
- `docs/implementation/phase-2-verification.md`;
- `schemas/project.schema.json`;
- `schemas/media-probe.schema.json`;
- `schemas/ingest-manifest.schema.json`;
- `src/inova_av/cli/main.py` se a interface do CLI tiver mudado.

## Exigir entradas

- diretório de projeto dentro de `workspace/`, com `project.yaml` válido e estado `received`;
- caminho local explícito da mídia;
- autorização explícita para processar aquela mídia;
- nome real do operador para `--authorized-by`.

Não aceitar rótulos genéricos como "Codex", "sistema" ou "automático" como identidade do autorizador.

## Fazer preflight

Executar na raiz do repositório:

```powershell
.\scripts\doctor.cmd --json
.\.venv\Scripts\inova-av.exe project validate <diretorio-do-projeto>
```

Confirmar que os caminhos e prefixos de FFmpeg/FFprobe correspondem a `config/pipeline.yaml`. Não usar outro executável encontrado casualmente no `PATH`.

## Executar a ingestão

Usar o único comando suportado atualmente:

```powershell
.\.venv\Scripts\inova-av.exe project ingest <diretorio-do-projeto> <midia-local> --authorized-by "Nome do operador" --json
```

Não copiar manualmente para contornar validações. Não alterar o original antes, durante ou depois da operação.

Interpretar códigos de saída:

- `0`: ingestão validada;
- `2`: entrada inválida ou quarentena controlada;
- `3`: FFmpeg/FFprobe ausente ou incompatível.

Tratar quarentena como resultado rastreável. Não corrigir, renomear ou repetir automaticamente o arquivo para "fazer passar".

## Verificar o resultado

1. Obter do resultado o caminho real do manifesto; não presumir nomes.
2. Validar os artefatos com o CLI:

```powershell
.\.venv\Scripts\inova-av.exe schema validate ingest-manifest <manifesto>
.\.venv\Scripts\inova-av.exe schema validate media-probe <relatorio-tecnico>
```

3. Confirmar que o manifesto registra autorização, versão das ferramentas, status, warnings, origem, SHA-256 e destino interno.
4. Em sucesso, confirmar proxy, relatório técnico e igualdade dos hashes exigidos pelo fluxo.
5. Em quarentena, confirmar estágio, motivo e ausência de commit parcial como projeto validado.
6. Preservar saídas dentro de `workspace/`; não adicionar mídia, proxy ou relatórios sensíveis ao Git.

## Não fazer

- transcrever, selecionar trechos, editar ou renderizar;
- chamar probe direto com argumentos improvisados quando o adapter existente atende;
- seguir symlink, escapar do workspace ou sobrescrever destino;
- apagar quarentena ou original;
- alegar compatibilidade geral de câmeras a partir do smoke sintético de um segundo.

## Concluir somente quando

- o comando e os schemas tiverem resultado coerente;
- hashes, paths, status e código de saída forem relatados sem expor dados sensíveis;
- a conclusão identificar se foi verificação estrutural, smoke sintético ou mídia real autorizada.
