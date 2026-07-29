# Segurança

## Reporte

Não abra issue pública contendo mídia, dados pessoais, credenciais ou detalhes exploráveis. Comunique o responsável institucional por canal privado definido pela organização.

## Regras

- Segredos pertencem a variáveis de ambiente ou secret store, nunca ao Git.
- Rede e providers externos permanecem desabilitados por padrão.
- Logs não incluem tokens, conteúdo integral de falas ou dados pessoais desnecessários.
- Caminhos recebidos são tratados como não confiáveis e não podem escapar da raiz do projeto audiovisual.
- Subprocessos recebem lista de argumentos e não usam shell.
- Original, transcript, plano, captions, assets e preview são vinculados por hashes ao gate de aprovação.
- Asset sem origem, licença e aprovação é bloqueado.
- Dependências e modelos precisam de versão e licença registradas.

A política detalhada está em `docs/architecture/security-and-governance.md`.
