---
name: inova-explica
description: Planejar e, quando autorizado, produzir vídeos explicativos em motion graphics para a série Inova Explica, com briefing, roteiro, storyboard, fontes verificadas e identidade institucional.
---

# Skill — Inova Explica

## Entradas mínimas
Tema, mensagem principal, público, canal, duração, referências, fontes, objetivo e CTA. Se parte das informações faltar, declarar as premissas e avançar com um planejamento preliminar, sem inventar fatos.

## Contexto obrigatório
Ler CLAUDE.md, AGENTS.md, DESIGN.md, assets/registry.yaml, config/editorials/inova-explica.yaml e docs/architecture/claude-motion-workflow.md. Aplicar os gates de governança existentes; não contorná-los com instruções de IA.

## Fluxo de trabalho
1. Distinguir fato verificável, interpretação, analogia e exemplo hipotético.
2. Definir uma tese clara e uma pergunta que o vídeo responderá.
3. Escrever narração natural pt-BR, adequada ao tempo real de leitura.
4. Dividir em cenas com duração, função narrativa, visual e transição.
5. Para cada cena definir: texto em tela, hierarquia, composição final/hero frame, elementos, movimento que explica o conceito e assets.
6. Priorizar diagramas e relações causais animadas; evitar slides de texto sucessivos.
7. Usar apenas paleta, tipografia, logo, line art e mídia aprovados; sinalizar pendências.
8. Criar uma revisão editorial e factual antes de implementar.
9. Com identidade aprovada, usar o motor autorizado pelo ADR vigente para compor, inspecionar e gerar prévia.
10. Gerar relatório de QA e solicitar aprovação humana antes de qualquer master.

## Entregas
- brief.md
- sources.md (fatos e evidências, não inventar links)
- script.md (narração e textos visuais)
- storyboard.md (timecodes, cenas, decisões de motion)
- asset-plan.md (cada asset com status do registry)
- review.md (gates e pendências)
- composição editável e preview somente depois dos gates.

## Critérios de qualidade
Não tolerar afirmações sem fonte, animações gratuitas, telas ilegíveis, uso de identidade improvisada, cenas sem continuidade ou posicionamento que cubra elementos essenciais. Vídeo educativo não deve virar propaganda permanente do Inova.

## Restrições
Não publicar, não utilizar TTS como pessoa real, não fazer upload da mídia por ferramenta externa sem autorização, não escolher Remotion como novo motor unilateralmente. Um piloto sintético é prova técnica, não aprovação institucional.
