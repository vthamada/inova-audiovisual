# ADR-0003 — Motor de renderização

- Status: Aceito
- Data: 2026-07-29
- Decisores: equipe Inova Diamantina
- Aprovação: usuário, 2026-07-29

## Contexto

O MVP precisa cortar, reenquadrar, normalizar áudio, aplicar legendas e inserir identidade audiovisual. FFmpeg cobre mídia com eficiência. HyperFrames fornece composições HTML/GSAP, lint, inspeção de layout/contraste, preview e render, mas requer Chrome Headless Shell e está sujeito ao ambiente de browser.

## Decisão

Usar dois níveis coordenados:

1. FFmpeg/FFprobe como motor canônico de mídia, áudio, cortes, captions e empacotamento.
2. HyperFrames como motor de motion templates para lower thirds, aberturas, encerramentos e overlays aprovados.

O adapter HyperFrames recebe apenas dados aprovados e não decide cortes. Para um template simples, FFmpeg pode compor diretamente; quando houver motion, HyperFrames gera camada ou composição intermediária que FFmpeg integra ao master.

Na Fase 1:

- fixar HyperFrames como dependência npm local;
- provisionar o Chrome Headless Shell pelo mecanismo oficial;
- usar Node 24 LTS;
- exigir `lint`, `validate` e `inspect` antes de render;
- desabilitar telemetria antes de material real;
- registrar versão do browser e do motor;
- criar `DESIGN.md` aprovado antes de qualquer composição.

Docker será opção de render reproduzível, não requisito do fluxo interativo inicial.

## Determinismo

- proibir aleatoriedade e relógio sem seed;
- fixar FPS, dimensões, fontes, assets e versões;
- manter timelines síncronas e finitas;
- usar hashes de todos os assets;
- gerar draft, standard e final com perfis explícitos;
- declarar se a garantia é semântica/técnica ou byte a byte;
- reservar render byte-idêntico para container por digest e golden test compatível.

## Consequências positivas

- qualidade visual evolui por templates;
- conteúdo fica separado da apresentação;
- FFmpeg continua responsável pelas operações críticas de mídia;
- inspeção visual automatizada reduz overflow e contraste inadequado;
- NLE continua opcional.

## Consequências negativas

- browser e Node aumentam o setup;
- duas etapas de composição podem aumentar disco e tempo;
- atualizações do browser podem alterar pixels;
- a máquina deve limitar workers para evitar pressão de RAM.

## Fallback

Se o benchmark HyperFrames falhar em estabilidade ou qualidade no Windows, o MVP continua com identidade estática em FFmpeg/ASS. Isso reduz motion, mas preserva ingestão, transcrição, edição, revisão e gate. A decisão de trocar o motor exigirá novo ADR.

## Critérios de aceite

- `doctor` sem dependência crítica ausente;
- composição vertical mínima passa em lint/validate/inspect;
- preview e render são válidos pelo FFprobe;
- áreas seguras e contraste passam em golden frames;
- uso de CPU, RAM, disco e tempo são medidos;
- execução offline após provisionamento;
- telemetria desabilitada;
- nenhum asset não registrado.

## Referências

- Instalação: <https://hyperframes.video/docs/getting-started/install>
- CLI: <https://hyperframes.video/docs/workflow/cli-reference>
