# Inventário de dependências de composição

## Runtime JavaScript local

| Dependência | Versão fixada | Finalidade | Licença revisada | Controles |
|---|---:|---|---|---|
| `hyperframes` | `0.7.82` | Motor principal de composição e QA local | Apache-2.0, conforme ADR-0005 | Único motor; telemetria desabilitada; sem upgrade automático |
| `gsap` | `3.15.0` | Timeline de animação complementar ao HyperFrames | Standard No Charge GSAP License, revisada em 2026-07-31 | Uso permitido para este Reel institucional; não usar para criar editor visual concorrente; carregar somente de `node_modules` |

## Registro de inclusão do GSAP

- **Autorização:** responsável institucional autorizou a emenda de política e o próximo passo controlado em 2026-07-31.
- **Origem:** npm registry, metadados consultados antes da instalação; tarball com integridade registrada no `package-lock.json`.
- **Escopo:** animações de interface na composição HyperFrames. Não é motor de vídeo, provider externo nem serviço de IA.
- **Runtime:** caminho local `node_modules/gsap/dist/gsap.min.js`; CDN, fontes, mídia, scripts e APIs remotos permanecem proibidos.
- **Segurança:** `npm install --save-exact gsap@3.15.0` reportou zero vulnerabilidades em 2026-07-31. Nenhum script pendente foi autorizado durante a instalação.
- **Limite de licença:** o uso comercial do GSAP é permitido pela licença padrão; a restrição relevante é não usá-lo para construir um produto concorrente de editor visual de animações. O pipeline do Inova produz composições institucionais e não oferece esse produto.

Qualquer alteração de versão, plugin adicional ou dependência transitiva material exige nova revisão de licença, integridade, compatibilidade com Node 24 e o gate de QA definido no ADR-0005.
