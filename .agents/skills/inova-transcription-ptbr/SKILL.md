---
name: inova-transcription-ptbr
description: Preparar, executar e revisar transcrição local pt-BR no pipeline audiovisual do Inova Diamantina. Usar para extração de áudio destinada a ASR, faster-whisper local, timestamps, confiança, transcript JSON, SRT/VTT, revisão humana ou diagnóstico de qualidade da fala.
---

# Transcrição pt-BR Inova

Usar `$inova-audiovisual-governance` antes desta skill. Tratar toda saída automática como rascunho não aprovado.

## Ler antes de agir

- `docs/decisions/ADR-0002-transcription-provider.md`;
- `config/pipeline.yaml`, seção `transcription`;
- `schemas/transcript.schema.json`;
- `src/inova_av/ports/providers.py` e o adapter de transcrição, quando existir;
- `README.md` para confirmar o estágio implementado do pipeline.

## Confirmar capacidade implementada

Verificar se existe comando ou adapter versionado para transcrição. No baseline da Fase 2 essa etapa ainda não está implementada.

Se continuar ausente:

- não instalar `faster-whisper`, modelo ou skill;
- não improvisar um script avulso;
- não processar mídia;
- registrar que a capacidade está pendente e indicar os contratos já definidos.

Prosseguir somente após implementação e verificação próprias da fase correspondente.

## Exigir gates de execução

- projeto em `validated` e mídia previamente ingerida;
- autorização explícita para material real;
- provider local aprovado e versão fixada;
- modelo já provisionado fora do Git;
- `local_files_only: true` e rede negada;
- processamento da cópia interna ou proxy, nunca do original externo.

Não usar API remota como fallback automático.

## Produzir transcript fiel

1. Registrar provider, modelo, revisão, device e compute type reais.
2. Fixar idioma de reconhecimento em português e emitir `language: pt-BR` no contrato.
3. Vincular `source_sha256` ao artefato efetivamente transcrito.
4. Preservar segmentos em ordem, com `0 <= start < end`, sem sobreposição indevida e dentro da duração da mídia.
5. Preservar timestamps e confiança quando o provider os fornecer; usar `null` quando não houver confiança, sem inventar valores.
6. Marcar fala incompreensível ou termo incerto explicitamente. Não completar pelo contexto.
7. Manter nomes, cargos, datas, instituições e termos territoriais para revisão humana obrigatória.
8. Criar a primeira versão com `review.status: pending`, `reviewed_by: null` e `reviewed_at: null`.

Validar a saída:

```powershell
.\.venv\Scripts\inova-av.exe schema validate transcript <transcript.json>
```

## Revisar sem apagar rastreabilidade

- comparar transcript com áudio, especialmente em trechos críticos;
- incrementar a versão ao corrigir conteúdo material;
- identificar o revisor e timestamp somente após revisão humana efetiva;
- derivar SRT/VTT do transcript validado, sem torná-los fonte de verdade separada;
- manter fala literal separada de texto editorial, síntese ou legenda adaptada.

## Não fazer

- tratar ASR como fato aprovado;
- corrigir citação por plausibilidade;
- ocultar incerteza ou baixa confiança;
- avançar para plano editorial com transcript ainda `pending`;
- baixar modelo ou habilitar rede sem autorização específica;
- armazenar áudio, modelos, cache ou transcript sensível no Git.

## Concluir somente quando

- schema e invariantes temporais passarem;
- provider e hash da fonte estiverem registrados;
- o status de revisão corresponder ao trabalho humano realmente concluído;
- limitações de qualidade e classe de evidência forem informadas.
