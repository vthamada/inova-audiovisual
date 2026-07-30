---
name: inova-render-verification
description: Verificar preview, draft e candidato a render final do pipeline audiovisual do Inova Diamantina. Usar para lint, validate e inspect do HyperFrames, FFprobe, loudness, captions, áreas seguras, golden frames, hashes, manifestos, approval.json, classificação de evidência ou handoff técnico.
---

# Verificação de Render Inova

Usar `$inova-audiovisual-governance` antes desta skill. Verificar; não publicar e não aprovar em nome de pessoa.

## Ler antes de agir

- `docs/decisions/ADR-0003-render-engine.md`;
- `docs/decisions/ADR-0004-human-approval-gate.md`;
- `DESIGN.md`;
- `schemas/render-request.schema.json`;
- `schemas/render-result.schema.json`;
- `schemas/render-manifest.schema.json`;
- `schemas/approval.schema.json`;
- `src/inova_av/domain/approval.py`;
- `docs/operations/troubleshooting.md`.

Usar `$hyperframes-cli` para a verificação específica do motor quando houver composição HyperFrames.

## Identificar o estágio

Classificar explicitamente o artefato como:

- **preview:** inspeção visual, não distribuível;
- **draft:** render para revisão, inequivocamente identificado como rascunho;
- **final candidate:** saída técnica ainda dependente do gate humano íntegro;
- **final rendered:** somente após aprovação vigente e render final bem-sucedido.

Não promover um estágio por nomenclatura de arquivo.

## Verificação estrutural

1. Validar request, resultado, manifesto e aprovação aplicáveis pelo CLI `schema validate`.
2. Confirmar que os paths permanecem confinados ao projeto e os arquivos existem.
3. Recalcular SHA-256 de inputs, outputs, registry e artefatos vinculados.
4. Conferir versões exatas de Python, Node, HyperFrames, browser, FFmpeg e FFprobe.
5. Em HyperFrames, exigir `lint`, `validate` e `inspect` antes de preview ou render.
6. Confirmar que não há URLs, fontes, scripts ou assets remotos.
7. Registrar comandos como arrays de argumentos, sem segredos.

Falha estrutural impede qualquer promoção.

## Smoke sintético

Executar somente com fixture sintética e identificada. Verificar no mínimo:

- duração, dimensões, FPS, codecs, pixel format e streams pelo FFprobe;
- áudio presente quando exigido, loudness dentro do perfil aprovado e ausência de clipping material;
- captions presentes, sincronizadas e legíveis;
- áreas seguras, contraste e overflow em frames representativos;
- início e fim da timeline, além de frames de transição;
- consumo de tempo, RAM e disco quando o teste for benchmark.

Não usar smoke sintético como evidência de qualidade com fala, câmera ou acústica reais.

## Verificar draft

- exigir edit-plan válido e composição aprovada para draft;
- manter identificação inequívoca de revisão;
- permitir `approval_sha256: null` somente quando `render_kind` for `draft`;
- gerar resultado e manifesto coerentes;
- encaminhar para revisão sem chamar o artefato de final.

## Verificar candidato final

Antes do render final:

1. confirmar projeto em `approved`;
2. validar `approval.json` e decisão `approved`;
3. conferir identidade do revisor, timestamp, direitos de imagem e revisão jurídica;
4. recalcular os hashes de transcript, edit-plan, captions, template config, assets registry e preview;
5. executar o gate de `src/inova_av/domain/approval.py` pelo caso de uso oficial quando ele estiver exposto;
6. bloquear diante de qualquer divergência, warning material ou capacidade ainda não implementada.

Se o comando oficial de render final ou o adapter ainda não existir, parar. Não improvisar um render externo e não fabricar manifesto de sucesso.

Após sucesso, validar:

```powershell
.\.venv\Scripts\inova-av.exe schema validate render-result <render-result.json>
.\.venv\Scripts\inova-av.exe schema validate render-manifest <render-manifest.json>
```

Confirmar que `approval_sha256` corresponde ao arquivo efetivamente usado. Render final não altera estado para `published`.

## Relatar evidência

Entregar separadamente:

- verificações executadas e códigos de saída;
- artefatos e hashes;
- warnings aceitos, rejeitados ou pendentes;
- gates de identidade e aprovação;
- classe de evidência: estrutural, smoke sintético ou material real autorizado;
- limitações que impedem alegação de produção.

## Não fazer

- aprovar, publicar, enviar ou distribuir;
- aceitar warning material sem decisão registrada;
- renderizar final sem `approval.json` íntegro;
- modificar artefato depois de aprovado sem invalidar a aprovação;
- armazenar renders, frames, mídia ou logs sensíveis no Git.

## Concluir somente quando

- todos os contratos e hashes aplicáveis forem coerentes;
- o estágio declarado corresponder à evidência;
- nenhuma pendência for ocultada;
- publicação permanecer uma ação humana separada.
