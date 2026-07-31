# Auditoria do pacote de referências visuais

**Data da análise:** 2026-07-29
**Escopo:** direção visual e prontidão de assets para o pipeline audiovisual
**Resultado:** baseline visual consolidada e assinatura canônica resolvida; assets ainda não elegíveis para render de produção

## Método

- leitura integral das 780 linhas do design system v2.0;
- renderização e inspeção visual das 16 páginas do guia PDF A4;
- inspeção das nove imagens apresentadas nas solicitações;
- coleta local de dimensão, tamanho e SHA-256, sem envio a serviço externo;
- comparação entre texto prescritivo, guia visual e aplicações de referência.

O PDF é composto por páginas rasterizadas: não há texto extraível nem estrutura marcada. Ele foi avaliado pelas páginas renderizadas, não apenas por metadados.

## Inventário

| ID | Arquivo | Formato / dimensão | SHA-256 | Papel | Elegível para produção? |
|---|---|---:|---|---|---|
| REF-DOC-01 | `Design_System_Visual_Editorial_Multicanal_Inova_Diamantina_V2.md` | Markdown, 21.846 bytes | `e5fbbdf972bee70188471eda6d98f4d81ed5d29648c6cb6f7c8449be1c72e8a3` | fonte prescritiva v2.0 | não é asset de render |
| REF-DOC-02 | `Guia_Visual_Editorial_Inova_Diamantina.pdf` | PDF A4, 16 páginas, 13.669.893 bytes | `194082ea2c43e604e4cfa303709446ac126889c44e782e0d9004914dcbab98ad` | guia visual e exemplos | não; páginas rasterizadas |
| REF-IMG-01 | `codex-clipboard-fa5b858f-0c01-40d4-802d-895cc6887c25.png` | 941 × 1672, 2.360.664 bytes | `1f3f9bdfe883a2045a78b7e5a656ba61ed1f8ba74b9de9090d760ec83359ac03` | “O movimento continua” / social | não; aplicação de referência |
| REF-IMG-02 | `codex-clipboard-d22ab151-85cc-4f38-9997-048e59f72740.png` | 941 × 1672, 2.307.619 bytes | `fcef71e0a2ab045c2de7ff6a7c263b99b5742cd95bc98b91603aad8f168a207b` | “Vozes do Ecossistema” | não; aplicação de referência |
| REF-IMG-03 | `codex-clipboard-da36276e-529e-45ca-baa6-911e2241d541.png` | 941 × 1672, 2.238.902 bytes | `a50ae04ddec33665597de7241ab7796902f0716b412692b1578b0973c5950035` | “Inova na Mídia” | não; aplicação de referência |
| REF-IMG-04 | `codex-clipboard-3d8530f4-11d9-48d5-a04d-02ea2c595cf8.png` | 941 × 1672, 2.429.755 bytes | `761ef29702d1e80d7ce5a3abe6fcbe6c2ceb30fd8a8d1cde8f9d5b93cab217f` | “Rede em Movimento” | não; aplicação de referência |
| REF-IMG-05 | `codex-clipboard-b7659c46-6aba-4fc8-aa1d-861c8e252911.png` | 941 × 1672, 2.387.413 bytes | `d7ac31b92b31178aa6fe348139a0736036e7ed6f3ae98b705440c5789748133a` | “Inova Explica” | não; aplicação de referência |
| REF-IMG-06 | `codex-clipboard-a6ab1b2b-3e53-4dd0-9bff-77678d7cccfd.png` | 941 × 1672, 2.289.730 bytes | `5ae0f8d6d1a13b60be61be6e54b403feff51f85fbd13516996abe6ab6c2a29b3` | abertura oficial 9:16 | não; aplicação de referência |
| REF-IMG-07 | `a74cd666-86f0-4f42-9c23-344c5d18aeb3.png` | 1672 × 941, 2.239.983 bytes | `5fb8cca57f004cb4540dade419a57ea771c65e8fc3541c0d96afbfa8e5108e0e` | line art panorâmica | autorizado e registrado como `brand.line-art-diamantina` em 2026-07-31 |
| REF-IMG-08 | `file_00000000307471f587f96259db355542.png` | 1536 × 1024, 111.111 bytes | `825fc15a9e8cce99638b2cefaa4380a546c8874809f4e7c0290adfc90e94cd0d` | identidade do evento encerrado “Pacto pela Inovação” | uso apenas histórico; não usar como assinatura institucional |
| REF-IMG-09 | `file_000000001f80720ebd694e22fb2f8b99 - Editado (1).png` | 1536 × 1024, RGBA transparente, 252.273 bytes | `4bf0152f36efca1d1f91677f238dd4170e4f75cb010ea117853da109e714a962` | logo horizontal “Ecossistema de Inovação” | autorizado e registrado em `assets/brand/` |

## Convergências verificadas

Os materiais concordam nos seguintes pontos:

- base clara com amplo espaço negativo;
- azul-marinho como cor de autoridade;
- azul, turquesa e verde como progressão de conexão e futuro;
- line art de Diamantina como âncora territorial;
- redes e nós nos cantos superiores;
- ondas fluidas em camadas no rodapé;
- tipografia sem serifa, com títulos curtos e dominantes;
- editorias em cápsulas, cards arredondados e ícones lineares;
- uma mensagem central por peça;
- tom institucional, humano, coletivo e orientado à ação;
- uso obrigatório de fotos reais quando pessoas e acontecimentos reais são o conteúdo.

## Decisão resolvida e lacunas

### 1. Assinatura da marca — resolvida

O guia PDF e as aplicações usam **“Ecossistema de Inovação”**. Uma referência horizontal anterior usava **“Pacto pela Inovação”**.

**Decisão institucional registrada em 2026-07-29:** `Ecossistema de Inovação` é a assinatura canônica e permanente. `Pacto pela Inovação` foi um evento já encerrado e deve aparecer somente em conteúdo retrospectivo ou documental sobre ele.

O novo PNG confirma visualmente a assinatura canônica e possui transparência real (RGBA, canal alfa de 0 a 255). Seu uso institucional foi autorizado explicitamente pelo usuário em 2026-07-29; a cópia verificada por SHA-256 foi registrada como `brand.logo-horizontal-ecossistema`.

### 2. Tipografia — pendente

Montserrat, Inter, Manrope e Source Sans 3 aparecem como sugestões. Nenhuma família, peso ou arquivo é declarado como oficial.

**Decisão necessária:** selecionar família e pesos, fornecer arquivos quando aplicável e registrar licença.

### 3. Formatos-fonte — parcialmente atendido

Foi fornecido um PNG horizontal transparente da assinatura canônica. Ainda não foram fornecidos SVGs, versões positiva/negativa/monocromática, arquivos editáveis de ondas/redes/ícones nem masters 1080 × 1920.

**Decisão necessária:** fornecer o banco oficial em formato-fonte, sem usar recorte ou vetorização automática das referências.

### 4. Origem e direitos

Os arquivos não trazem licença, autoria, responsável pela aprovação, validade ou restrições de uso.

**Decisão necessária:** registrar proveniência, licença, crédito, restrições, aprovador e data no `assets/registry.yaml`.

### 5. Motion e safe areas

As peças definem direção estática, mas não especificam medidas de área segura, timing, easing, intensidade ou regras de adaptação para 16:9.

**Decisão necessária:** aprovar hero frames por formato e, a partir deles, tokens de movimento.

## Atualização de governança em 2026-07-31

Ricardo Hamada autorizou o uso institucional do arquivo de line art e aprovou a direção visual do perfil vertical de Reel. A cópia fornecida foi adicionada a `assets/brand/` sem alteração e registrada como `brand.line-art-diamantina`, com o mesmo SHA-256 de `REF-IMG-07`.

Dois ornamentos próprios, `generated.inova-network-corners` e `generated.inova-wave-footer`, foram criados localmente em SVG a partir da direção visual documentada. Eles não reutilizam nem recortam as aplicações de referência e constam no registry com origem, licença, aprovador, data, restrições e hashes. As aplicações rasterizadas permanecem inelegíveis como assets finais.

## Decisão de governança

Dos nove PNGs analisados, o logo horizontal `Ecossistema de Inovação` e a line art panorâmica foram copiados para `assets/`, após autorização explícita. Os checksums das cópias coincidem com os originais e suas entradas constam em `assets/registry.yaml`. As aplicações rasterizadas e a identidade do evento continuam apenas como referências externas.

O pacote já é suficiente para substituir uma direção visual genérica por uma baseline específica no `DESIGN.md`. Ele ainda não é suficiente para iniciar uma composição institucional ou um render final.

## Handoff necessário

Para abrir o gate visual, a equipe responsável deve fornecer ou confirmar:

1. fornecer símbolo e versões positiva, negativa e monocromática, preferencialmente em SVG;
2. fornecer line art, ondas, redes e ícones em arquivos-fonte;
3. definir tipografia e pesos oficiais, com licença;
4. aprovar áreas seguras por formato;
5. aprovar padrões de abertura, lower third, legenda e encerramento;
6. registrar aprovadores e datas dos demais assets.
