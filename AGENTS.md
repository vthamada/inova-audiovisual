# Instruções locais

## Escopo e segurança

- Não execute `git init` e não crie repositório aninhado.
- Não mova código para o repositório do portal.
- Não processe ou publique mídia real sem autorização explícita.
- Não altere originais; trabalhe em cópias verificadas por SHA-256.
- Não envie arquivos a serviços externos com `network_policy: deny_by_default`.
- Não armazene segredos, mídia, modelos, caches ou renders no Git.
- Não crie composição HyperFrames antes da aprovação de `DESIGN.md` e dos assets.
- Não permita render final sem `approval.json` íntegro.

## Toolchain

- Use Python 3.12 no `.venv`.
- Use Node 24 LTS e dependências npm locais.
- No PowerShell, use `npm.cmd` e `npx.cmd`; scripts `.ps1` podem ser bloqueados pela política do host.
- Nunca presuma qual FFmpeg está no `PATH`; valide caminho e versão.

## Verificação obrigatória

Após mudanças Python: pytest, Ruff e mypy. Após mudanças HyperFrames: doctor e, quando houver composição, lint, validate e inspect antes de preview/render.

Toda conclusão deve distinguir teste estrutural, smoke test sintético e validação com material real autorizado.
