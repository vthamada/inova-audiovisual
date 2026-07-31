# ADR-0005 — Estratégia de skills e motor principal de vídeo

- Status: Aceito para o MVP
- Data: 2026-07-30
- Decisores: equipe Inova Diamantina
- Relacionados: ADR-0001, ADR-0002, ADR-0003 e ADR-0004

## Contexto

O ecossistema de Agent Skills oferece frameworks de composição local, como HyperFrames
e Remotion, e serviços completos server-side, como VideoDB. Instalar vários motores
parece ampliar capacidades, mas também duplica DSLs, dependências, licenças, QA,
templates e caminhos de render. Para o Inova, essa duplicação aumenta risco sem resolver
um requisito ainda não atendido.

O pipeline já adota Python para domínio, FFmpeg/FFprobe para mídia e HyperFrames para
motion. Ele precisa permanecer local-first, funcionar no Windows, negar rede por padrão,
preservar originais e bloquear render final sem aprovação vinculada a hashes.

A avaliação completa está em `docs/architecture/skills-evaluation.md`.

## Decisão

Adotar **HyperFrames como único motor principal de composição programática e motion**.

Manter FFmpeg/FFprobe como camada canônica de processamento e empacotamento de mídia.
Essa camada não é um segundo motor criativo e não recebe responsabilidade por templates
sofisticados quando HyperFrames for aplicável.

Não instalar nem manter Remotion em paralelo. Não integrar VideoDB ao baseline local.
Serviços remotos e outros motores somente poderão ser avaliados por provider isolado,
com autorização explícita, dados não sensíveis, orçamento e novo ADR.

Criar seis skills específicas do projeto em `.agents/skills`:

1. `inova-audiovisual-governance`;
2. `inova-ingest-and-probe`;
3. `inova-transcription-ptbr`;
4. `inova-editorial-edit-plan`;
5. `inova-hyperframes-brand-motion`;
6. `inova-render-verification`.

Essas skills devem complementar, e não duplicar, as skills upstream. Elas codificam
política institucional, ordem do workflow, contratos, gates e critérios de evidência.

## Motivos

- HyperFrames já está fixado, testado estruturalmente e alinhado ao adapter existente;
- HTML/CSS/GSAP é adequado ao authoring por agente e aos elementos editoriais do Inova;
- lint, validate, inspect e preview formam um QA visual mais direto para o workflow atual;
- Apache-2.0 traz custo e licença mais previsíveis que a licença especial do Remotion;
- execução local evita envio de mídia e mantém `network_policy: deny_by_default`;
- Remotion acrescentaria React e bundler sem substituir FFmpeg ou Python;
- VideoDB requer credencial e processamento server-side, incompatível com o baseline;
- um único motor reduz drift de templates, dependências e competências operacionais.

## Emenda de 2026-07-31 — dependências complementares locais

O responsável institucional autorizou a reformulação da política que vedava qualquer pacote para concluir a composição. A regra passa a distinguir **motor de vídeo** de **runtime complementar local**.

Continua proibida a instalação de Remotion, VideoDB, outro motor de composição, template externo ou upgrade não planejado do HyperFrames. Passa a ser permitido adicionar uma dependência complementar ao HyperFrames — como GSAP — quando houver autorização explícita do responsável e forem cumpridos todos os controles a seguir:

1. versão exata declarada em `package.json` e `package-lock.json`;
2. licença, integridade, dependências transitivas e compatibilidade com Node 24 revisadas antes do uso;
3. execução inteiramente local por arquivo presente em `node_modules`, sem CDN, fonte, script, mídia ou API remota;
4. ausência de telemetria, credencial, provider externo, upload ou egress de mídia;
5. validação por `lint`, `validate` e `inspect` antes de qualquer preview;
6. atualização do inventário de supply chain e revisão do diff antes da publicação.

Essa emenda não autoriza render final, publicação ou envio de material real; esses atos continuam regidos pelo ADR-0004 e pelos gates de aprovação.

## Restrições obrigatórias

- fixar HyperFrames em versão exata e revisar upgrades;
- permitir somente dependência complementar local que satisfaça a emenda acima; ela não pode se tornar um segundo motor;
- manter telemetria desabilitada;
- proibir assets, fontes, scripts e mídia remotos nas composições institucionais;
- revisar qualquer item de registry antes de importação;
- não criar composição antes da aprovação de `DESIGN.md` e assets;
- exigir lint, validate e inspect antes de preview/render;
- registrar versões, hashes e FFprobe dos outputs;
- não processar material real sem autorização explícita;
- não permitir render final sem `approval.json` íntegro;
- distinguir verificação estrutural, smoke sintético e validação real autorizada.

## Consequências positivas

- uma única gramática de composição e um único conjunto de templates;
- menor superfície de dependências, licenças e supply chain;
- compatibilidade com a arquitetura já implementada;
- skills do Inova podem concentrar governança sem reimplementar o motor;
- execução offline e custo local previsível após provisionamento;
- fallback estático em FFmpeg/ASS continua disponível se o browser falhar.

## Consequências negativas

- HyperFrames ainda está na série `0.x` e publica releases em ritmo elevado;
- Node e Chrome Headless aumentam consumo e manutenção;
- a equipe não obtém o ecossistema React e a maturidade comercial do Remotion;
- busca semântica e percepção multimodal de acervos não entram prontas como no VideoDB;
- qualidade final ainda depende de assets, fontes, safe areas e motion aprovados;
- a decisão precisa ser reavaliada se o benchmark Windows não atingir os critérios.

## Alternativas rejeitadas

### HyperFrames e Remotion simultâneos

Rejeitada por duplicar motor, runtime visual, templates, testes e manutenção. Não há
requisito que justifique dois frameworks de composição.

### Remotion como motor principal

É tecnicamente forte e bem mantido, mas exigiria migração, React/bundler, revisão de
licença e novo adapter. Não apresentou vantagem comprovada suficiente sobre o stack já
preparado.

### VideoDB como plataforma principal

Rejeitada por exigir API key e upload/processamento server-side. A licença MIT da skill
não elimina custos, termos, retenção, residência de dados ou dependência do serviço.

### FFmpeg como único motor visual

Rejeitada para motion completo porque filtergraphs são difíceis de revisar e manter e
não oferecem o mesmo loop de layout, contraste e preview. FFmpeg permanece essencial na
camada técnica e como fallback estático.

## Critérios de reavaliação

Reabrir esta decisão se ocorrer qualquer um destes eventos:

- HyperFrames deixar de ser mantido ou mudar de licença;
- regressão não contornável no Windows ou no Chrome fixado;
- benchmark sintético e piloto autorizado falharem em qualidade ou estabilidade;
- custo operacional do render local ultrapassar alternativa comprovada;
- requisito aprovado depender de capacidade exclusiva de outro motor;
- política institucional autorizar processamento remoto com DPA e orçamento;
- Remotion oferecer benefício material demonstrado que justifique migração total.

Uma reavaliação deve comparar migração completa; não deve introduzir um segundo motor
principal silenciosamente.

## Estado de implementação

Esta ADR registra estratégia. Ela não autoriza composição, instalação ou mídia real por si só. A emenda de 2026-07-31 permite dependência complementar local somente quando houver autorização explícita e todos os controles definidos acima forem atendidos.
HyperFrames `0.7.82` permanece fixado. As seis skills específicas foram implementadas em
`.agents/skills` em 2026-07-30, sem dependências, scripts duplicados ou assets adicionais.
