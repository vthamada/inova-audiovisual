# Análise de opções técnicas

## Critérios

As opções foram comparadas considerando Windows como plataforma prioritária, funcionamento offline, auditabilidade, fidelidade das falas, determinismo, qualidade visual, curva operacional, portabilidade para worker/n8n e possibilidade de acabamento profissional.

## Opção A — Python e FFmpeg como núcleo exclusivo

Um CLI Python orquestra ingestão, FFprobe, áudio, transcrição, análise, cortes, legendas ASS e render por filtros FFmpeg.

### Pontos fortes

- menor número de runtimes;
- excelente controle de mídia e automação;
- bom comportamento offline;
- processos e manifestos fáceis de auditar;
- adequado a cortes, áudio, legendas e composição visual simples.

### Limitações

- motion design sofisticado fica difícil de manter em filtergraphs;
- evolução de templates tende a gerar comandos longos e frágeis;
- preview e inspeção visual são menos amigáveis;
- identidade audiovisual pode ficar tecnicamente correta, porém rígida.

### Adequação

Boa base de mídia, mas insuficiente como solução visual completa para as editorias previstas.

## Opção B — Orquestração Python + FFmpeg + HyperFrames

Python controla domínio, estados, providers, arquivos e FFmpeg. Um adapter chama um workspace Node/HyperFrames para motion templates, lower thirds, encerramentos e inspeção visual. Os dois runtimes trocam contratos JSON versionados e arquivos de mídia, não objetos internos.

### Pontos fortes

- usa cada runtime na área em que é mais forte;
- preserva FFmpeg como base madura de mídia;
- permite templates codificados, versionados e determinísticos;
- oferece lint, validação, inspeção headless, preview e render;
- separa conteúdo editorial da apresentação;
- adapta-se ao Modo A e ao Modo B;
- mantém DaVinci/Premiere como acabamento opcional.

### Limitações

- exige Python e Node versionados;
- precisa de adapter robusto de subprocesso;
- Chrome Headless Shell adiciona peso operacional;
- composição byte a byte idêntica depende de ambiente fixado, fontes e container;
- há mais superfície para upgrades coordenados.

### Adequação

É a opção recomendada. O custo adicional é justificável pela identidade visual e pela evolução para editorias recorrentes.

## Opção C — Node/HyperFrames como orquestrador dominante

Node controla ingestão, estado, render e integrações; Python é chamado apenas para transcrição ou visão computacional.

### Pontos fortes

- integração direta com HyperFrames;
- ecossistema único para CLI e templates;
- boa experiência para desenvolvimento visual.

### Limitações

- análise de áudio, ML e manipulação estruturada de mídia têm melhor oferta em Python;
- providers de transcrição exigem processos laterais ou bindings;
- aumenta a chance de o motor visual contaminar regras de domínio;
- não elimina FFmpeg nem Python no MVP real.

### Adequação

Viável, mas menos equilibrada para o conjunto de responsabilidades do pipeline.

## Opção D — Pipeline centrado em editor profissional ou SaaS

DaVinci Resolve, Premiere, CapCut ou serviço SaaS concentra montagem, legendas e acabamento, com scripts auxiliares para ingestão e exportação.

### Pontos fortes

- melhor interface para decisões narrativas e acabamento manual;
- recursos maduros de cor, máscara e multicâmera;
- adoção rápida em produção assistida.

### Limitações

- automação e determinismo variam por produto e licença;
- maior dependência de interface, formato proprietário ou serviço externo;
- menor auditabilidade do caminho completo;
- não atende bem ao Modo B desacoplado;
- mudanças de plataforma e políticas podem quebrar o fluxo.

### Adequação

Camada opcional de acabamento e exceções, não núcleo institucional.

## Matriz comparativa

Escala: 1 = fraco, 3 = aceitável, 5 = forte.

| Critério | A: Python/FFmpeg | B: Híbrida | C: Node dominante | D: NLE/SaaS |
|---|---:|---:|---:|---:|
| Mídia e áudio | 5 | 5 | 3 | 5 |
| Motion templates | 2 | 5 | 5 | 5 |
| Determinismo | 5 | 4 | 4 | 2 |
| Auditabilidade | 5 | 5 | 4 | 2 |
| Offline | 5 | 5 após provisionamento | 4 | 2–4 |
| Portabilidade para worker | 5 | 5 | 5 | 2 |
| Acabamento manual | 2 | 4 | 3 | 5 |
| Complexidade operacional | 4 | 3 | 3 | 3 |
| Governança e gate | 5 | 5 | 4 | 3 |
| Adequação global ao MVP | 4 | 5 | 3 | 3 |

## Recomendação

Adotar a Opção B com limites claros:

- Python é dono do domínio, workflow, schemas, auditoria e providers;
- FFmpeg/FFprobe são o motor de mídia e áudio;
- HyperFrames é um adapter de apresentação, não o banco de verdade editorial;
- JSON/YAML e arquivos de mídia são as interfaces;
- DaVinci/Premiere recebem exportações futuras, sem se tornarem dependência do MVP;
- serviços externos permanecem desligados por padrão.

## Decisões que dependem de validação

- benchmark `faster-whisper` `small` versus `medium` em pt-BR;
- teste visual de HyperFrames com o Chrome Headless Shell provisionado;
- template oficial, fontes e áreas seguras após recebimento dos assets;
- perfil de Quick Sync versus `libx264` em qualidade, estabilidade e tempo;
- formato inicial de intercâmbio com NLE: EDL, FCPXML ou ambos;
- orçamento de armazenamento após medição com vídeos reais.
