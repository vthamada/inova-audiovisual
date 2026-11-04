---
name: inova-factual-check
description: Verificar afirmações, datas, números, instituições, cargos, fontes e riscos de interpretação em roteiros, legendas e cards da série Inova Explica e de vídeos institucionais.
---

# Skill — revisão factual e institucional

Ler CLAUDE.md e AGENTS.md. Validar narrativas com o contexto institucional e as fontes efetivamente disponíveis.

## Procedimento
1. Extrair todas as afirmações verificáveis do roteiro: datas, cifras, leis, resultados, beneficiários, instituições, programas e atribuições.
2. Para cada afirmação, registrar fonte primária, URL ou documento, data da evidência e grau de confiança.
3. Separar: fato confirmado, informação sem evidência, proposta futura, hipótese didática e opinião.
4. Verificar se a instituição correta é realizadora, apoiadora, parceira ou somente mencionada.
5. Evitar personalismo e usar a assinatura canônica Inova Diamantina — Ecossistema de Inovação.
6. Comparar texto de narração com texto em tela para prevenir distorções.
7. Bloquear produção final quando um dado material não estiver verificado ou houver divergência não resolvida.
8. Registrar correções e encaminhar para validação humana.

## Regras de proteção
Não inventar fontes, resultados, falas, parcerias, estatísticas, cargos ou links. Não usar notícia antiga como fato atual. Não usar acesso externo de mídia, transcrições ou dados internos sob network_policy deny_by_default. Pesquisa de informações públicas só quando permitida e sempre com registro de proveniência.

## Saída
Uma tabela no documento sources.md com: afirmação, tipo, evidência, data, status e ação. Não tratar roteiro revisado por IA como aprovação institucional.
