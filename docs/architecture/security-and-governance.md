# Segurança e governança

## Objetivos

Proteger pessoas, falas, credenciais, originais, direitos de imagem, identidade institucional e rastreabilidade. O pipeline deve reduzir trabalho sem transformar inferências automáticas em decisões institucionais.

## Classificação de dados

| Classe | Exemplos | Regras mínimas |
|---|---|---|
| Pública aprovada | vídeo final publicado, release aprovado | distribuição conforme canal |
| Institucional interna | preview, briefing, checklist | acesso da equipe e retenção definida |
| Pessoal/sensível | bruto, voz, rosto, contato, bastidor | acesso mínimo, não enviar externamente por padrão |
| Segredo | API keys, tokens, credenciais | somente secret store/env; nunca Git, logs ou manifestos |
| Asset licenciado | logos, fontes, trilhas | uso condicionado ao registro de origem e licença |

## Ameaças prioritárias

1. Publicação sem aprovação ou com autorização de imagem pendente.
2. Corte que altera o sentido de uma fala.
3. Envio silencioso de mídia a serviço externo.
4. Vazamento de segredo em Git, log ou comando.
5. Substituição ou corrupção do original.
6. Uso de logo, fonte ou trilha sem origem/licença.
7. Path traversal, arquivo malformado ou consumo excessivo de recursos.
8. Supply chain de Python, npm, modelos e browser.
9. Aprovação aplicada a artefatos diferentes dos revisados.
10. Prompt injection dentro de transcript, metadados ou documentos recebidos.

## Controles obrigatórios

### Originais

- copiar para `source/` sem transcodificar;
- calcular SHA-256 antes e depois da cópia;
- nunca sobrescrever;
- limitar todas as saídas ao diretório do projeto;
- usar nome interno seguro e preservar o nome original somente como metadado;
- quarentenar incompatibilidade de hash, arquivo truncado ou estrutura suspeita.

### Rede e providers

- `network_policy: deny_by_default`;
- provider local como padrão;
- provider remoto exige configuração explícita, finalidade e aceite;
- log de egress registra provider, região quando conhecida, arquivo/hash, data e ator, sem gravar segredo;
- modo offline impede resolução remota e falha com mensagem acionável;
- transcript ou metadado recebido nunca pode alterar ferramentas, comandos ou política.

### Segredos

- `.env` ignorado e `.env.example` sem valores reais;
- preferir secret store do worker em Modo B;
- mascarar variáveis sensíveis em logs;
- não interpolar entrada em shell;
- subprocessos recebem listas de argumentos e `shell=False` no Python;
- comandos documentados e manifestos são sanitizados.

### Aprovação

O gate final exige simultaneamente:

- transcrição marcada como revisada;
- plano e preview revisados;
- autorização de imagem `approved`;
- assets com licença e aprovação válidas;
- checklist institucional completo;
- `approval.json` assinado logicamente pelo revisor;
- hashes atuais iguais aos aprovados;
- estado `approved`.

Qualquer alteração invalida a aprovação. O MVP não terá bypass. Uma futura política de emergência exigirá duas pessoas, justificativa e evento separado.

### Fidelidade

- transcript literal e texto editorial são campos distintos;
- cada segmento preserva origem e timecode;
- o review mostra contexto removido;
- nomes, cargos, datas e instituições são fatos pendentes até confirmação;
- proibir clonagem de voz, modificação de rosto e fala sintética;
- conteúdo gerado por IA, se futuramente permitido, deverá ser identificado e não poderá representar pessoa real.

### Assets

`assets/registry.yaml` deverá conter:

- `asset_id` e versão;
- arquivo e SHA-256;
- origem;
- titular/licença;
- escopo territorial, canais e expiração quando aplicável;
- crédito necessário;
- aprovador e data;
- restrições de transformação.

Asset sem registro não entra em render institucional. Logos nunca são recriados por IA. `DESIGN.md` é gate para composição HyperFrames.

## Supply chain

- lockfiles para Python e npm;
- hashes quando a ferramenta suportar;
- versões exatas para HyperFrames, schemas e modelos;
- registro de licença de dependências e modelos;
- browser provisionado por comando documentado;
- SBOM e varredura de vulnerabilidades antes de releases;
- Docker image por digest para render reproduzível;
- upgrades feitos em branch com golden tests.

Node 25 do host não deve ser adotado por estar EOL. O projeto propõe Node 24 LTS. O snapshot FFmpeg ativo e a instalação duplicada devem ser substituídos por uma escolha versionada e verificada.

## Telemetria e privacidade

Antes de processar material real:

- desabilitar telemetria do HyperFrames;
- verificar telemetria de outras ferramentas;
- documentar qualquer dado técnico ainda enviado;
- não usar TTS, MusicGen, HeyGen ou serviços equivalentes no MVP;
- não manter preview público ou servidor de preview acessível fora de `localhost`.

## Retenção, backup e descarte

A política final depende da equipe e da base legal. Até aprovação:

- não apagar automaticamente originais ou revisões;
- não tratar Git como storage de mídia;
- manter manifests e auditoria junto ao pacote;
- backups devem preservar criptografia e controle de acesso;
- descarte futuro deve ser explícito, auditado e recuperável conforme política;
- `.gitignore` deve excluir workspace, mídia, cache, modelos, renders e segredos.

## Logs

Logs estruturados registram:

- `run_id`, `project_id`, etapa e estado;
- timestamps com fuso;
- duração;
- ferramenta e versão;
- input/output por ID e hash;
- avisos e erro;
- ator humano ou worker.

Logs não registram conteúdo integral da fala, contatos, tokens, caminhos externos desnecessários ou parâmetros secretos.

## Responsabilidades humanas

| Decisão | Responsável humano |
|---|---|
| Autorizar imagem e uso de voz | responsável designado |
| Confirmar nomes, cargos e fatos | editor/revisor |
| Aprovar corte e contexto | editor |
| Aprovar identidade e assets | comunicação/gestão da marca |
| Aprovar risco jurídico | responsável jurídico quando acionado |
| Aprovar versão institucional | aprovador designado |
| Publicar | operador autorizado, fora do MVP |

## Pendências de governança

- base legal, termo e evidência de autorização de imagem;
- papéis nominais e segregação de funções;
- prazo de retenção de brutos, previews e logs;
- política de backup e criptografia;
- canais permitidos para providers externos;
- lista oficial de logos, fontes, trilhas e licenças;
- critérios para revisão jurídica;
- regras de uso de materiais com menores de idade.
