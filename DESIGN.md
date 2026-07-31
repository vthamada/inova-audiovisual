# Identidade audiovisual — baseline documentada, gate de produção pendente

**Status:** aprovado para composições e previews institucionais em 2026-07-31. O render final continua condicionado ao `approval.json` íntegro e ao checklist humano do projeto; esta aprovação não o substitui.

Este arquivo traduz o `Design System Visual, Editorial e Multicanal — Inova Diamantina v2.0`, o `Guia Visual e Sistema Editorial` de 16 páginas e as referências visuais entregues para regras aplicáveis ao pipeline audiovisual. O inventário e a análise de prontidão estão em `docs/audiovisual/visual-reference-audit.md`.

## Hierarquia das fontes

Quando houver conflito, seguir esta ordem:

1. assets oficiais em formato-fonte, com licença e aprovação registradas;
2. decisão escrita do responsável institucional;
3. design system v2.0;
4. guia visual editorial;
5. imagens de referência, usadas apenas como direção e nunca como fonte oficial.

Uma divergência não deve ser resolvida por aproximação. Ela interrompe o uso do elemento até validação humana.

**Registro de aprovação:** Ricardo Hamada, 2026-07-31. Escopo: direção visual do Reel institucional em preparação. Essa decisão não cria, licencia ou registra automaticamente arquivos de fonte, line art, ondas, redes ou ícones que ainda não estejam no repositório.

## Gate de identidade

| Item | Situação | Decisão atual |
|---|---|---|
| narrativa e atributos da marca | documentado | pode orientar roteiro, layout e revisão |
| paleta e função das cores | documentado | tokens definidos abaixo |
| vocabulário visual | documentado | pode orientar protótipos de layout |
| assinatura da marca | resolvido em 2026-07-29 | `Ecossistema de Inovação` é a assinatura institucional canônica |
| identidade do evento | resolvido em 2026-07-29 | `Pacto pela Inovação` identifica um evento encerrado e não substitui a assinatura institucional |
| logo oficial | atendido para o perfil atual | PNG horizontal RGBA transparente autorizado e registrado; SVG e demais versões não são exigidos enquanto não forem usados |
| tipografia | atendido para preview local | `Segoe UI` instalada no Windows, em pesos regular e semibold; não é declarada como fonte canônica da marca |
| line art, ondas e redes | atendido para o perfil atual | line art fornecida e dois ornamentos SVG originais registrados, com origem, licença, aprovação e hashes |
| áreas seguras por formato | atendido para Reel | perfil 1080 × 1920: 96 px laterais, 180 px superiores e 300 px inferiores; demais formatos ficam pendentes |
| linguagem de movimento | atendido para Reel | tokens de preview registrados abaixo, aplicáveis somente ao perfil vertical atual |
| responsável e data de aprovação | atendido | Ricardo Hamada, 2026-07-31 |

Somente arquivos autorizados e registrados em `assets/registry.yaml` podem entrar em render. Capturas de referência seguem excluídas como assets finais. O perfil de Reel pode usar apenas o logo horizontal, a line art e os dois ornamentos locais registrados.

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

Para o perfil de preview aprovado:

- usar `"Segoe UI", system-ui, sans-serif`, disponível localmente no Windows, em `400`, `600` e `700`;
- tratar a escolha como substituição operacional de preview, não como declaração de tipografia canônica;
- não baixar fontes, usar CDN ou incorporar arquivos remotos;
- manter H1 curto, forte e dominante;
- usar H2 para explicar e organizar;
- limitar corpo a texto objetivo e legível em celular;
- reservar microtexto para legenda, categoria e CTA funcional;
- usar caixa alta e tracking apenas em rótulos curtos, nunca em parágrafos.

## Gramática visual

Elementos recorrentes registrados para o perfil atual:

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

### Perfil de Reel aprovado

- **Safe area:** 96 px nas laterais, 180 px no topo e 300 px na base em 1080 × 1920. A base reserva a interface do Instagram e a área de assinatura.
- **Entradas:** `0.36s` a `0.56s`, `power3.out`, opacidade e deslocamento vertical máximo de 28 px.
- **Transições:** dissolução suave com deslocamento vertical de `0.42s`, `sine.inOut`; cenas de um mesmo bloco preservam o conteúdo até o início da transição.
- **Ondas e rede:** movimento contínuo, determinístico e de baixa amplitude; nunca mais de 10 px de deslocamento por ciclo e sem loop infinito em render.
- **Lower third:** faixa de leitura na área segura inferior, nome em `700`, função em `400`, duração mínima de 3 s e contraste auditável sobre um gradiente azul-marinho.
- **Legendas:** centralizadas na área segura inferior acima do lower third, no máximo duas linhas, fundo/contorno suficiente para contraste e sem encobrir rostos.
- **Abertura e encerramento:** assinatura com logo horizontal preservado; o termo `Pacto pela Inovação` só aparece na abertura documental deste Reel, pois retrata o evento encerrado.

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
- [ ] símbolo, versões positiva, negativa e monocromática, preferencialmente em SVG (não usados no perfil atual);
- [x] tipografia operacional de preview, pesos e disponibilidade local documentados;
- [x] line art, ondas e redes do perfil atual com origem, licença e aprovação;
- [ ] áreas seguras para 1920 × 1080 e 1080 × 1080 (não usadas neste Reel);
- [x] áreas seguras para 1080 × 1920;
- [x] regras de lower third, legenda, abertura e encerramento;
- [x] tokens de motion para o perfil de Reel;
- [x] responsável institucional e data de aprovação;
- [x] entradas correspondentes em `assets/registry.yaml`.

O gate está aberto para composições e previews do perfil de Reel acima. Uma peça em outro formato, uma fonte oficial, novos assets ou qualquer render final exige nova confirmação e os respectivos gates.
