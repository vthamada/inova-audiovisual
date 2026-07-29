# Identidade audiovisual — baseline documentada, gate de produção pendente

**Status:** direção visual consolidada em 2026-07-29; **ainda não aprovada para composições ou renders institucionais**.

Este arquivo traduz o `Design System Visual, Editorial e Multicanal — Inova Diamantina v2.0`, o `Guia Visual e Sistema Editorial` de 16 páginas e as referências visuais entregues para regras aplicáveis ao pipeline audiovisual. O inventário e a análise de prontidão estão em `docs/audiovisual/visual-reference-audit.md`.

## Hierarquia das fontes

Quando houver conflito, seguir esta ordem:

1. assets oficiais em formato-fonte, com licença e aprovação registradas;
2. decisão escrita do responsável institucional;
3. design system v2.0;
4. guia visual editorial;
5. imagens de referência, usadas apenas como direção e nunca como fonte oficial.

Uma divergência não deve ser resolvida por aproximação. Ela interrompe o uso do elemento até validação humana.

## Gate de identidade

| Item | Situação | Decisão atual |
|---|---|---|
| narrativa e atributos da marca | documentado | pode orientar roteiro, layout e revisão |
| paleta e função das cores | documentado | tokens definidos abaixo |
| vocabulário visual | documentado | pode orientar protótipos de layout |
| assinatura da marca | resolvido em 2026-07-29 | `Ecossistema de Inovação` é a assinatura institucional canônica |
| identidade do evento | resolvido em 2026-07-29 | `Pacto pela Inovação` identifica um evento encerrado e não substitui a assinatura institucional |
| logo oficial | parcialmente atendido | PNG horizontal RGBA transparente autorizado e registrado; SVG e demais versões ainda pendentes |
| tipografia | pendente | o material lista opções, mas não escolhe uma família canônica |
| line art, ondas e redes | pendente | confirmar arquivos-fonte, origem, licença e restrições |
| áreas seguras por formato | pendente | aprovar medidas para 16:9, 9:16 e 1:1 |
| linguagem de movimento | parcialmente documentado | direção qualitativa abaixo; tempos e easings aguardam aprovação |
| responsável e data de aprovação | pendente | registrar no gate antes da primeira composição |

Somente arquivos autorizados e registrados em `assets/registry.yaml` podem entrar em render. O logo horizontal canônico já está registrado; as demais referências continuam excluídas e as pendências restantes mantêm fechado o gate da primeira composição.

### Regra de assinatura

- Usar **Inova Diamantina — Ecossistema de Inovação** na comunicação institucional permanente.
- Tratar **Pacto pela Inovação** como identidade histórica de um evento encerrado, somente em conteúdo retrospectivo ou documental sobre aquele evento.
- Não usar a arte do Pacto como logo principal do ecossistema.

## Style prompt

Identidade institucional, clara e contemporânea, com forte respiro sobre fundo branco gelo. O sistema conecta patrimônio e futuro por meio da line art de Diamantina, redes e nós tecnológicos, ondas fluidas azul–turquesa–verde, ícones lineares e títulos de alta hierarquia. A presença territorial deve ser reconhecível sem cair em nostalgia; a tecnologia deve parecer humana, colaborativa e pública, nunca gamer, futurista genérica ou excessivamente corporativa.

## Narrativa e atributos

**Narrativa central:** “Diamantina: onde o passado encontra o futuro.”

A comunicação deve transmitir:

- construção coletiva e permanente;
- institucionalidade com energia e proximidade;
- conexão entre pessoas, ideias, instituições e oportunidades;
- territorialidade contemporânea;
- clareza, utilidade, continuidade e confiança.

Evitar personalismo, autopromoção, promessas não validadas e linguagem tecnicista sem explicação.

## Cores

```css
:root {
  --inova-navy: #081858;
  --inova-deep-blue: #041A43;
  --inova-institutional-blue: #0868C8;
  --inova-support-blue: #0072CE;
  --inova-mid-blue: #0095C8;
  --inova-turquoise: #0898A8;
  --inova-light-turquoise: #00A4A8;
  --inova-green: #79C143;
  --inova-ice: #F7F9FB;
  --inova-light-gray: #EEF2F6;
  --inova-white: #FFFFFF;
}
```

### Funções

- `--inova-navy` e `--inova-deep-blue`: títulos, autoridade, rodapés e contraste principal.
- `--inova-institutional-blue` e `--inova-support-blue`: destaques, links, ícones e linhas.
- `--inova-mid-blue`: apoio digital e transições cromáticas.
- `--inova-turquoise` e `--inova-light-turquoise`: tecnologia, conexão e transições.
- `--inova-green`: futuro, sustentabilidade e chamadas positivas; usar como acento, não como massa de texto.
- `--inova-ice`, `--inova-light-gray` e branco: base, respiro, divisores e cards.

Gradientes azul–turquesa–verde devem ficar em palavras-chave, cápsulas, CTAs, ondas e acentos. Não usar gradiente como fundo integral concorrendo com o conteúdo. Todo texto deve passar pela auditoria de contraste do HyperFrames; a presença da cor na paleta não garante legibilidade em qualquer combinação.

## Tipografia

O sistema exige uma família sem serifa, moderna e legível. O documento cita **Montserrat, Inter, Manrope e Source Sans 3 como sugestões**, não como escolha oficial.

Até a aprovação:

- não fixar uma dessas famílias em composição institucional;
- não presumir pesos ou licenças;
- manter H1 curto, forte e dominante;
- usar H2 para explicar e organizar;
- limitar corpo a texto objetivo e legível em celular;
- reservar microtexto para legenda, categoria e CTA funcional;
- usar caixa alta e tracking apenas em rótulos curtos, nunca em parágrafos.

## Gramática visual

Elementos recorrentes, após registro como assets oficiais:

- logo e símbolo/diamante tecnológico;
- elementos de rede e nós, preferencialmente nos cantos e áreas de respiro;
- line art de Diamantina como âncora territorial;
- ondas fluidas azul–verde, normalmente no rodapé;
- ícones lineares;
- cards e cápsulas arredondados;
- linhas e pontos finos para organizar leitura;
- textura clara e discreta, sem ruído visual.

### Arquitetura de layout

1. Uma mensagem central por peça ou cena.
2. Marca/cabeçalho, editoria, título, apoio, visual, serviço e CTA em ordem clara.
3. Margens amplas e conteúdo construído primeiro no hero frame.
4. Preferência por alinhamento à esquerda em informação editorial; centralização é adequada para abertura e assinatura.
5. Line art e ondas não podem reduzir a área útil nem disputar atenção com o título.
6. Cards agrupam informação; não devem virar decoração repetitiva.
7. Textos longos migram para legenda, site, carrossel ou documento.

### Padrões observados nas referências 9:16

- grande área de respiro na metade superior ou central;
- redes nos cantos superiores;
- marca no topo ou antes do bloco editorial;
- título dominante em azul-marinho, com uma linha ou palavra em gradiente;
- line art de Diamantina no terço inferior;
- ondas em camadas no fechamento;
- cápsula curta para editoria e CTA discreto.

Esses padrões são direção visual. As referências têm 941 × 1672 px e não substituem masters 1080 × 1920 nem definem áreas seguras finais.

### Padrões 16:9

A referência horizontal comprova a viabilidade da line art panorâmica e de uma assinatura centralizada. Ela não define, sozinha, template de vídeo, lower third ou safe area. Esses componentes devem ser aprovados em hero frames antes de animação.

## Tradução para movimento

Quando o gate for aprovado, o motion deve reforçar conexão, fluxo e construção coletiva:

- desenhar linhas e acender nós de maneira sequencial e determinística;
- revelar a line art com máscara suave ou traçado progressivo;
- mover ondas lentamente em camadas, com pequena diferença de velocidade;
- usar entradas claras por hierarquia: editoria, título, apoio e CTA;
- manter movimentos fluidos, precisos e sóbrios;
- preservar o hero frame estático como fonte de verdade do layout;
- usar transições entre cenas sem esvaziar a cena anterior antes da transição.

Tempos, distâncias, easings e intensidade ainda não são tokens oficiais. Até a aprovação, não extrapolar a direção qualitativa para uma composição institucional.

## Pessoas, fotografia e IA

- Pessoas, reuniões, rádio, visitas, eventos e bastidores exigem foto original.
- Não gerar nem substituir pessoas reais por IA.
- Foto real é protagonista, com gradiente inferior apenas quando necessário à leitura.
- Categoria pode entrar em cápsula; título e apoio devem ser curtos.
- IA pode apoiar fundos abstratos, tecnologia e ilustração conceitual sem pessoas identificáveis, desde que o uso seja aprovado.
- Nunca recriar a logo por IA.

## O que não fazer

- usar screenshot, página do guia ou imagem de referência como asset final;
- redesenhar, vetorizar automaticamente ou completar a logo por IA;
- usar `Pacto pela Inovação` como assinatura institucional permanente, em agenda corrente ou fora do contexto histórico do evento;
- usar estética gamer, neon excessivo, glitch, 3D genérico ou efeitos chamativos sem função;
- poluir a peça com muitos ícones, texturas, gradientes ou mensagens;
- usar verde e turquesa em texto sem contraste suficiente;
- deixar fundos, line art ou ondas competir com o conteúdo;
- gerar pessoas para substituir registros reais;
- produzir composição com fonte, logo ou elementos gráficos não licenciados;
- transformar todo conteúdo em um template idêntico.

## Gate para a primeira composição

Antes de criar HTML HyperFrames, registrar:

- [x] assinatura canônica: `Ecossistema de Inovação`; `Pacto pela Inovação` reservado ao evento encerrado;
- [x] logo horizontal canônico em PNG transparente, autorizado e registrado;
- [ ] símbolo, versões positiva, negativa e monocromática, preferencialmente em SVG;
- [ ] família tipográfica, pesos, arquivos e licença;
- [ ] line art, ondas, redes e ícones com origem e licença;
- [ ] áreas seguras para 1920 × 1080, 1080 × 1920 e 1080 × 1080;
- [ ] regras de lower third, legenda, abertura e encerramento;
- [ ] tokens de motion ou aprovação de protótipos de hero frame;
- [ ] responsável institucional e data de aprovação;
- [ ] entradas correspondentes em `assets/registry.yaml`.

Somente depois desse checklist o status deste arquivo pode mudar para **aprovado para composições**.
