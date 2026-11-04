---
name: inova-motion-qa
description: Revisar criticamente motion graphics e vídeos programáticos do Inova, conferindo tipografia, segurança de tela, ritmo, contraste, frames reais, áudio, conformidade e evidências de render.
---

# Skill — QA audiovisual

Antes de qualquer avaliação, ler CLAUDE.md, AGENTS.md, DESIGN.md, SECURITY.md, o contrato de canal e os ADRs aplicáveis.

## Dois níveis de revisão
1. Técnica: composição renderiza, codec/fps/duração/resolução, áudio, caminhos e assets íntegros.
2. Editorial e visual: clareza, hierarquia tipográfica, ritmo, movimento semântico, coerência, legibilidade, identidade, fontes e direitos.

Aprovação técnica NÃO substitui aprovação institucional.

## Método
- Confirmar gates de design, assets, consentimento e aprovação.
- Inspecionar hero frame de cada cena e pelo menos oito timestamps distribuídos na timeline; amostrar adicionalmente transições e pontos de maior densidade textual.
- Conferir vídeo no formato final e em escala aproximada de smartphone.
- Verificar texto fora da tela, clipping, contraste insuficiente, disputas visuais, safe areas e logo deformada.
- Confirmar tempos de leitura, continuidade entre cenas, excesso de efeitos, cortes bruscos e música competindo com voz.
- Conferir o arquivo real com FFprobe e registrar comandos/versões usados.
- Executar lint/validate/inspect do motor, quando disponível, sem confundir verificações automáticas com revisão humana.
- Documentar cada falha por timestamp, gravidade, causa e correção recomendada.

## Relatório obrigatório
- evidências realmente coletadas;
- tabela de achados com timestamp e severidade (bloqueante, maior, menor);
- critérios de aceitação aprovados/reprovados;
- pendências de design, direitos e factualidade;
- decisão: revisão necessária / elegível a revisão humana;
- nunca declarar publicação autorizada por conta própria.

## Proteção
Não incluir frames de pessoas nem mídias sensíveis em PRs ou issues públicos. Guardar provas visuais locais em pasta ignorada, vinculando manifestos permitidos.
