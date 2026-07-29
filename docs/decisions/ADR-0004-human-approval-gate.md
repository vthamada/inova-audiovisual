# ADR-0004 — Gate de aprovação humana

- Status: Aceito
- Data: 2026-07-29
- Decisores: equipe Inova Diamantina
- Aprovação: usuário, 2026-07-29

## Contexto

Vídeos institucionais envolvem direitos de imagem, integridade de fala, fatos, reputação e licenças. Um simples campo `approved: true` pode permanecer válido após alterações e permitir que o render final não corresponda ao preview revisado.

## Decisão

Implementar um gate criptograficamente vinculado aos artefatos. A aprovação é um documento `approval.json` validado por schema que inclui:

- `project_id` e versão;
- revisor identificado;
- timestamp com fuso;
- decisão;
- checklist obrigatório;
- autorização de imagem;
- hashes SHA-256 do transcript revisado, edit plan, captions, template config, assets e preview;
- observações e requisitos de revisão jurídica;
- versão da política.

O caso de uso `render final` recalcula todos os hashes e verifica o estado. Divergência invalida a aprovação e retorna o projeto para revisão. Não haverá bypass no MVP.

## Separação de ações

- `render-draft`: permitido após plano válido; sempre contém marca de revisão ou identificação inequívoca.
- `approve`: somente pessoa autorizada; não renderiza.
- `render-final`: somente com aprovação vigente.
- `mark-published`: confirmação manual posterior; não publica.

Essas ações não serão combinadas em um único comando.

## Checklist mínimo

- fala e contexto;
- nomes, cargos, datas e instituições;
- autorização de imagem;
- direitos de logos, fontes e trilhas;
- legendas;
- enquadramento e áreas seguras;
- áudio;
- identidade visual;
- risco jurídico/político quando aplicável;
- canal e duração.

## Consequências positivas

- o final corresponde ao que foi revisado;
- mudanças são detectadas;
- papéis e decisões ficam auditáveis;
- automação futura não reduz o controle humano.

## Consequências negativas

- qualquer correção exige nova aprovação;
- hashes e versões aumentam os artefatos;
- identidade do revisor requer política organizacional;
- assinatura criptográfica forte fica para fase posterior.

## Segurança

Editar manualmente `project.yaml` não concede aprovação. O CLI valida transição, permissões e hashes. No Modo B, identidade virá do sistema autenticado; no Modo A inicial, será uma identidade explícita local registrada no audit log. Aprovação não contém segredo.

## Critérios de aceite

Testes devem provar:

1. render final falha sem `approval.json`;
2. falha com autorização pendente;
3. falha com asset sem licença;
4. falha após alterar um byte de artefato aprovado;
5. falha se o estado não for `approved`;
6. sucesso com conjunto íntegro;
7. `published` não é alcançado pelo render;
8. erros explicam exatamente o gate ausente.
