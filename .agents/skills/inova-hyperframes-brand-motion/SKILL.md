---
name: inova-hyperframes-brand-motion
description: Criar e revisar hero frames, lower thirds, aberturas, encerramentos, overlays e motion institucional do Inova Diamantina com HyperFrames. Usar em qualquer composição visual programática da marca, adaptação 16:9 ou 9:16, timeline GSAP, template institucional ou inspeção de identidade audiovisual.
---

# Motion Inova com HyperFrames

Usar `$inova-audiovisual-governance` antes desta skill. Usar HyperFrames como único motor principal de composição; manter FFmpeg como camada de mídia.

## Ler antes de agir

- `DESIGN.md` por inteiro;
- `assets/registry.yaml`;
- `docs/audiovisual/visual-reference-audit.md`;
- `docs/decisions/ADR-0003-render-engine.md`;
- `docs/decisions/ADR-0005-video-skills-strategy.md`;
- o edit-plan e a configuração do canal aplicável;
- a skill upstream `$hyperframes` para authoring e `$hyperframes-cli` para comandos; usar `$gsap` quando a animação exigir timeline.

## Aplicar o gate visual antes de criar

Confirmar que `DESIGN.md` declara aprovação para composições e renders institucionais. Confirmar também:

- assets-fonte aprovados e registrados;
- fontes licenciadas e disponíveis localmente;
- áreas seguras por canal aprovadas;
- tokens de motion ou hero frames aprovados;
- entrada correspondente para cada asset em `assets/registry.yaml`.

Validar o registro:

```powershell
.\.venv\Scripts\inova-av.exe schema validate asset-registry assets\registry.yaml
```

Se qualquer item estiver pendente, parar antes de criar arquivo de composição e relatar exatamente o gate fechado. Não interpretar aprovação do PNG do logo como aprovação de todo o sistema visual.

## Preservar a identidade

- usar "Inova Diamantina — Ecossistema de Inovação" como assinatura institucional permanente;
- usar "Pacto pela Inovação" somente em conteúdo retrospectivo ou documental sobre o evento encerrado;
- preservar proporção, cor, tipografia e disposição do logo registrado;
- obter dimensões, FPS e duração dos contratos do canal e do edit-plan;
- usar referências visuais somente como direção, nunca como asset final;
- não gerar pessoas por IA nem substituir registro de direito de imagem.

## Criar de forma determinística

1. Começar pelo hero frame estático como fonte de verdade do layout.
2. Separar conteúdo aprovado de apresentação e manter dados externos à composição.
3. Usar somente arquivos locais, caminhos estáveis e assets com hash verificado.
4. Proibir CDN, Google Fonts, scripts remotos, URL de mídia e registry não revisado.
5. Proibir `Math.random`, relógio de parede e efeitos sem seed ou duração finita.
6. Usar GSAP com timelines explícitas, FPS e duração fixos.
7. Adaptar 16:9 e 9:16 como layouts deliberados; não apenas recortar o mesmo frame.
8. Limitar workers conforme `config/pipeline.yaml` e preservar a versão exata do HyperFrames.

Não instalar Remotion, VideoDB, pacote, template ou atualização para concluir a composição.

## Aplicar QA antes de preview

Usar o CLI local fixado pelo projeto e a skill `$hyperframes-cli` para executar, nesta ordem:

1. `lint`;
2. `validate`;
3. `inspect`;
4. preview somente após os três passarem ou após decisão explícita sobre warning não material.

Corrigir overflow, contraste, área segura, fonte ausente, mídia remota, timeline infinita e asset divergente antes de avançar. Não fazer render final nesta skill.

## Saídas permitidas

- composição e configuração versionáveis sem mídia incorporada;
- hero frames ou snapshots de revisão dentro de área ignorada pelo Git;
- relatório de lint, validate e inspect;
- lista de assets e hashes usados;
- pendências para aprovação humana.

## Concluir somente quando

- o gate visual estiver comprovadamente aberto;
- identidade, canal, assets e determinismo estiverem corretos;
- lint, validate e inspect tiverem evidência registrada;
- o resultado continuar classificado como composição ou draft, nunca como final aprovado.
