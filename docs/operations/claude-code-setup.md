# Setup do Claude Code para Inova Explica

**Ambiente-alvo:** Windows 11, PowerShell, repositório já clonado.  
**Status:** guia; nenhum plugin foi instalado automaticamente pelo commit.

## 1. Abrir a raiz existente

No terminal do workspace onde o projeto já foi clonado:

~~~powershell
git status
git remote -v
git branch --show-current
~~~

Confirmar que o remoto é vthamada/inova-audiovisual. Não executar git init nem copiar o projeto para outro repositório.

## 2. Verificar as ferramentas do baseline

~~~powershell
claude --version
.\scripts\doctor.cmd
.\scripts\verify.cmd
~~~

O repositório já fixa Python 3.12, Node 24 e HyperFrames 0.7.82. Consulte README.md e docs/operations/environment-setup.md antes de instalar ou atualizar dependências. Não executar npm install ou upgrades indiscriminados.

## 3. Instalação do plugin HyperFrames (mediante autorização do operador)

O plugin do Claude Code é separado da dependência local hyperframes do projeto. Usar o marketplace oficial, depois verificar status:

~~~powershell
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
claude plugin details hyperframes
~~~

Guia: https://github.com/heygen-com/hyperframes/blob/main/docs/guides/plugins.mdx

A instalação pode exigir rede e altera a configuração local do Claude. Não executá-la automaticamente em CI nem sem permissão do operador. A versão de runtime do projeto permanece fixada.

## 4. Remotion (somente avaliação)

Não instalar o plugin ou runtime Remotion como dependência de produção até revisar licença institucional e aprovar novo ADR. Se um benchmark for autorizado, o plugin oficial do Claude Code é:

~~~powershell
claude plugin marketplace add remotion-dev/claude-code-plugin
claude plugin install remotion@remotion
~~~

Documentação: https://www.remotion.dev/docs/ai/claude-code-plugin
Licença e elegibilidade: https://www.remotion.dev/docs/license/faq

Uma licença MIT para o plugin não equivale à licença de uso do runtime Remotion.

## 5. Iniciar sessão do Claude

Abrir Claude Code na raiz do repositório, que possui CLAUDE.md. Ele deverá ler AGENTS.md, SECURITY.md, DESIGN.md e os ADRs antes de modificar qualquer conteúdo.

Solicitação inicial sugerida:

"Leia CLAUDE.md, AGENTS.md, SECURITY.md, DESIGN.md, assets/registry.yaml e docs/implementation/inova-explica-pilot-01.md. Faça somente auditoria de prontidão para o piloto Inova Explica: enumere bloqueios de identidade, licenças, assets e render. Não instale nada e não crie composições. Proponha storyboard, hero frames como especificações documentais e plano de testes. Informe precisamente o que depende de aprovação humana."

## 6. Passos pós-aprovação (futuros)

1. Selecionar motor de composição autorizado e versionado.
2. Produzir componentes locais com assets registrados.
3. Executar QA do motor e inspeção de pelo menos oito timestamps.
4. Emitir preview para revisão humana.
5. Persistir evidências e correções.
6. Exportar master somente via gate de aprovação existente.

Não enviar arquivos de pessoas ou material reservado a ferramentas externas sem autorização própria. Não fazer commit de vídeos, áudios, fontes restritas, modelos, caches ou credenciais.

## 7. Verificação de problemas

Se o Claude falhar em encontrar skills, recarregar plugins e conferir sua instalação local. Se o diagnóstico do projeto falhar, resolver primeiro a toolchain do README. Não mascarar falhas com simuladores nem presumir sucesso sem execução.
