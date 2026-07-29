# ADR-0001 — Arquitetura central

- Status: Aceito
- Data: 2026-07-29
- Decisores: equipe Inova Diamantina
- Aprovação: usuário, 2026-07-29

## Contexto

O pipeline precisa operar primeiro de forma assistida no Windows e evoluir para worker/n8n sem reescrita. Deve processar mídia localmente, preservar falas, gerar templates institucionais e manter auditabilidade. FFmpeg é forte em mídia; Python é forte em workflow e ML; HyperFrames é adequado a motion templates codificados.

## Decisão

Adotar arquitetura local-first, orientada por arquivos e hexagonal:

- Python é o núcleo de domínio, aplicação, CLI, estado e providers;
- FFmpeg/FFprobe são adapters de mídia;
- Node/HyperFrames é adapter de apresentação e motion;
- YAML é usado para configuração humana;
- JSON versionado e validado por JSON Schema é usado para artefatos e contratos;
- JSONL append-only registra eventos;
- subprocessos trocam requests/results estruturados;
- não haverá banco de dados no MVP;
- Modo A e Modo B chamam os mesmos casos de uso.

Versões-base propostas:

- Python 3.12 em ambiente virtual isolado;
- Node 24 LTS com dependências locais;
- FFmpeg, HyperFrames, browser e modelos com versões explícitas.

## Consequências positivas

- regras de domínio independem de ferramentas;
- providers podem ser substituídos;
- arquivos facilitam revisão, backup e auditoria;
- o fluxo pode operar offline;
- worker futuro não duplica regras;
- templates visuais evoluem sem alterar transcript ou edit plan.

## Consequências negativas

- dois runtimes e FFmpeg precisam de coordenação;
- contratos entre processos exigem versionamento;
- ambiente de render precisa de browser;
- determinismo depende de versões, fontes e codecs fixados;
- storage por arquivos precisa de política de retenção.

## Alternativas rejeitadas

- FFmpeg exclusivo: motion design e preview limitados.
- Node dominante: pior equilíbrio para ML, áudio e domínio.
- NLE/SaaS como núcleo: menor determinismo, auditabilidade e portabilidade.
- Repositório do portal: proibido pelo limite organizacional já decidido.

## Critérios para aceitar

- concordância com a divisão Python/Node/FFmpeg;
- concordância com ausência de banco no MVP;
- concordância com Node 24 LTS e ambiente Python isolado;
- aprovação dos contratos por arquivo e da separação entre Modo A/Modo B.

## Critério de revisão futura

Reavaliar banco de dados ou fila apenas quando concorrência, busca multiusuário ou volume medido mostrarem limitação concreta. Reavaliar runtimes somente com benchmark e plano de migração.
