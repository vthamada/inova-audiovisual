---
name: inova-audiovisual-governance
description: Governar segurança, autorização, privacidade, integridade e aprovação no pipeline audiovisual do Inova Diamantina. Usar antes de qualquer atividade com mídia, áudio, transcrição, pessoas, assets, composição, render, handoff ou publicação, inclusive em análises e mudanças de código que possam afetar esses fluxos.
---

# Governança Audiovisual Inova

Aplicar esta skill primeiro. Tratar os gates como condições obrigatórias, não como recomendações.

## Ler antes de agir

Localizar a raiz pelo `AGENTS.md` e ler:

- `AGENTS.md`;
- `SECURITY.md`;
- `config/pipeline.yaml`;
- `docs/architecture/security-and-governance.md`;
- `docs/decisions/ADR-0004-human-approval-gate.md`;
- `src/inova_av/domain/states.py` quando houver mudança de estado;
- `src/inova_av/domain/approval.py` quando houver aprovação ou render final.

Ler também a documentação ou o schema da etapa solicitada. Não substituir contratos existentes por regras improvisadas na skill.

## Classificar o pedido

Determinar antes de qualquer escrita:

1. se a ação é somente leitura, altera artefatos ou produz saída audiovisual;
2. se o material é sintético, real autorizado, público aprovado, interno ou sensível;
3. se há pessoas identificáveis, voz, dados pessoais, direitos autorais ou revisão jurídica;
4. se a ação exige rede, provider externo, credencial ou upload;
5. qual é o estado atual e a próxima transição permitida do projeto;
6. se a evidência obtida será estrutural, smoke sintético ou validação real autorizada.

## Aplicar gates duros

- **Mídia real:** exigir autorização explícita para o material, finalidade e etapa. Exigir identidade nominal em operações que possuam `authorized_by`. Parar se faltar autorização.
- **Originais:** nunca editar, sobrescrever, renomear ou mover o original. Trabalhar somente na cópia interna criada pelo fluxo de ingestão e verificada por SHA-256.
- **Rede:** confirmar `network_policy: deny_by_default`. Não enviar mídia, áudio, transcrição, frames ou metadados a serviço externo. Autorização futura de egress deve ser específica, documentada e nunca implícita.
- **Segredos:** usar variável de ambiente ou secret store. Nunca registrar credenciais em Git, logs, manifestos, comandos ou respostas.
- **Assets:** usar somente arquivo registrado em `assets/registry.yaml`, com origem, licença, aprovação e SHA-256 válidos.
- **Pessoas:** confirmar direito de imagem e voz. Não gerar representação de pessoa real por IA.
- **Estado:** permitir somente transições presentes em `ALLOWED_TRANSITIONS`. Não editar `project.yaml` para simular autorização ou aprovação.
- **Aprovação:** não combinar `render-draft`, `approve`, `render-final` ou `mark-published`. Não permitir render final sem `approval.json` válido, decisão humana `approved` e hashes ainda íntegros.
- **Publicação:** não inferir autorização para publicar, enviar ou marcar como publicado.

## Executar o workflow

1. Fazer primeiro inspeções somente leitura.
2. Relatar gates satisfeitos, pendentes e bloqueados antes de uma ação material.
3. Invocar a skill específica da etapa e limitar a execução ao escopo autorizado.
4. Preservar hashes, versões, comandos e identidade do operador nos artefatos previstos pelos schemas.
5. Parar diante de estado incerto, hash divergente, quarentena, autorização vencida ou warning material.
6. Entregar um resumo com ação executada, artefatos, gates, limitações e classe de evidência.

## Proibir

- alterar originais ou contornar o ingest;
- usar fallback remoto silencioso;
- instalar provider, modelo, skill ou asset sem avaliação e autorização;
- armazenar mídia, modelos, caches, renders ou segredos no Git;
- chamar draft de final ou teste sintético de validação real;
- aprovar em nome de uma pessoa;
- publicar como efeito colateral de render ou handoff.

## Concluir somente quando

- o escopo autorizado estiver explícito;
- nenhum gate obrigatório tiver sido ignorado;
- os artefatos e estados corresponderem aos schemas vigentes;
- a conclusão distinguir claramente verificação estrutural, smoke sintético e validação real autorizada.
