---
name: inova-editorial-edit-plan
description: Criar e revisar planos editoriais de corte rastreáveis para vídeos do Inova Diamantina. Usar ao selecionar trechos de transcript revisado, definir hook, contexto, desenvolvimento e encerramento, preparar overlays e captions, adaptar duração por canal ou validar um edit-plan antes do draft.
---

# Plano Editorial Inova

Usar `$inova-audiovisual-governance` antes desta skill. Produzir plano validável; não cortar mídia nem renderizar.

## Ler antes de agir

- `docs/architecture/data-flow.md`;
- `schemas/transcript.schema.json`;
- `schemas/edit-plan.schema.json`;
- `src/inova_av/domain/states.py`;
- a configuração aplicável em `config/channels/`;
- a configuração aplicável em `config/editorials/`.

## Exigir entradas confiáveis

- projeto compatível com a etapa editorial;
- transcript cujo schema passe e cuja revisão humana esteja `reviewed`;
- mídia de origem vinculada pelo SHA-256 correto;
- canal, formato e objetivo editorial explícitos;
- duração-alvo obtida da configuração, não inventada.

Parar se o transcript estiver `pending`, se o hash não corresponder ou se o pedido depender de fala inaudível não revisada.

## Planejar sem alterar sentido

1. Identificar a tese editorial e o público sem transformar hipótese em fato.
2. Selecionar somente falas existentes no transcript revisado.
3. Registrar em cada segmento `source_file`, `in`, `out`, `purpose` e `transcript_excerpt`.
4. Garantir `0 <= in < out`, intervalos dentro da duração e ordem narrativa explícita.
5. Copiar `transcript_excerpt` literalmente do transcript revisado. Não reescrever uma citação para melhorar fluidez.
6. Usar `purpose` conforme o schema: `hook`, `context`, `development`, `closing` ou `other`.
7. Manter a soma e a estrutura dos segmentos compatíveis com a duração-alvo do canal.
8. Identificar texto criado pela equipe como overlay editorial, nunca como fala do entrevistado.
9. Apontar captions para um artefato derivado do transcript correto.
10. Criar o plano com `approval.status: pending` até decisão humana.

## Preservar contexto e território

- evitar corte que inverta opinião, causalidade, tempo verbal ou escopo da fala;
- manter ressalvas e condições materiais próximas do trecho principal;
- conferir nomes, cargos, datas e instituições nas fontes aprovadas do projeto;
- usar conexão territorial somente quando for concreta e verificável;
- tratar `Pacto pela Inovação` como evento encerrado, não como assinatura institucional permanente.

## Validar o contrato

Executar:

```powershell
.\.venv\Scripts\inova-av.exe schema validate edit-plan <edit-plan.json>
```

Além do schema, revisar manualmente:

- continuidade de sentido entre cortes;
- correspondência literal dos excerpts;
- duração e formato do canal;
- origem de overlays e captions;
- warnings editoriais ou jurídicos pendentes.

## Não fazer

- fabricar, parafrasear ou completar citação;
- selecionar trecho de transcript não revisado;
- aprovar o próprio plano em nome de pessoa;
- criar composição, draft, render final ou publicação;
- ocultar warning para permitir avanço de estado.

## Concluir somente quando

- o edit-plan passar no schema e na revisão semântica;
- todos os cortes forem rastreáveis ao transcript e à mídia;
- o status de aprovação refletir a decisão humana real;
- limitações e questões abertas estiverem registradas para a próxima etapa.
