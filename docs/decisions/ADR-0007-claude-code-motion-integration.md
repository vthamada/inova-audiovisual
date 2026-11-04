# ADR-0007 — Integração de Claude Code e avaliação de motores de motion

- Status: **Proposto — depende de aprovação humana**
- Data: 2026-11-04
- Escopo: editoria Inova Explica, plugins do Claude Code e estudos comparativos

## Contexto

O repositório já adotou Python + FFmpeg + HyperFrames como núcleo local-first e possui ADR-0003 aceito. A demanda atual é explorar a capacidade do Claude para roteiros, storyboards, motion graphics e revisão visual, com custo controlado e sem reconstruir o pipeline.

## Proposta

1. Acrescentar CLAUDE.md e skills de Claude para direção editorial, factualidade e QA.
2. Manter HyperFrames/FFmpeg como motor atual sem alterar suas versões.
3. Estudar Remotion apenas como benchmark independente e condicionado à elegibilidade de licença para o uso institucional.
4. Adotar o mesmo briefing, storyboard e critérios de avaliação em qualquer benchmark comparativo.
5. Integrar qualquer futura implementação aos estados, schemas, registry, aprovação humana e auditoria existentes.
6. Não ativar publicação automática nem permitir envio de mídia real a provedores remotos sem autorização específica.

## Alternativas

A. Permanecer com HyperFrames, mas dirigir e refinar a produção com Claude Code — preferência inicial, menor risco de integração.
B. Experimento isolado com Remotion depois da revisão de licença — útil para comparação de qualidade editorial e produtividade.
C. Substituir HyperFrames por Remotion no pipeline principal — não recomendado sem resultado comparativo, decisão institucional e plano de migração.

## Critérios para decidir uma eventual mudança

- qualidade visual avaliada em escala de smartphone;
- fidelidade ao design system;
- reutilização e manutenção dos componentes;
- duração de implementação;
- estabilidade de preview/render no Windows;
- custo total/licenciamento;
- operação offline e controle de dados;
- compatibilidade com schemas e approval.json;
- evidências reais de QA.

## Consequências

Nenhuma mudança no motor aceito ocorre com esta proposta. O arquivo CLAUDE.md é orientação compatível com os gates existentes e não autoriza composição antes da aprovação do DESIGN.md. Decisões de troca de motor exigem ADR posterior ou atualização formal deste ADR com aprovação explícita.

## Próxima decisão humana necessária

Homologar tipografia, motion tokens, áreas seguras e assets; confirmar situação de licença Remotion; autorizar um piloto sem material sensível.
