# Claude Code no pipeline audiovisual — integração proposta

**Data:** 2026-11-04  
**Finalidade:** acrescentar um fluxo de produção visual para Inova Explica sem substituir os módulos, contratos e gates existentes.  
**Natureza:** especificação de integração, não instalação nem migração aprovada.

## Diagnóstico do repositório existente

O projeto já possui CLI Python, schemas, ingestão/FFprobe, faster-whisper local, revisão de transcript, testes, CI, assets registrados, configuração de editorias e HyperFrames fixado via npm. A estrutura está além de um scaffold inicial. Deve ser preservada.

Fontes de verdade:
- AGENTS.md / SECURITY.md / config/pipeline.yaml;
- DESIGN.md / assets/registry.yaml;
- docs/decisions/ADR-0001 a ADR-0006;
- src/inova_av, schemas e respectivos testes.

## Papel do Claude

Claude Code é agente de desenvolvimento e direção assistida: pesquisa técnica permitida, roteiro, storyboard, especificação de componentes, implementação após autorização, inspeção de renders e propostas de correção. Não é um serviço de renderização autônomo e não substitui o processo humano de aprovação.

O acesso do Claude ao repositório e a contratação do serviço não autorizam transferir mídia, transcrições, entrevistas ou dados pessoais para fornecedores externos. Respeitar o modelo de dados local e a política deny_by_default.

## Fluxo proposto para Inova Explica

Tema/fonte verificada
  -> brief com público, canal, duração e CTA
  -> roteiro de narração e texto em tela
  -> storyboard com cenas e hero frames
  -> planejamento de assets licenciados
  -> revisão factual, identidade e autorização
  -> composição no motor autorizado
  -> lint/validate/inspect + preview
  -> inspeção humana do vídeo
  -> ajustes, novo preview
  -> aprovação humana com hashes
  -> render final pelo fluxo existente.

O novo fluxo deve reutilizar os schemas e estados existentes. Se o formato de storyboard ou composição exigir campos adicionais, propor contrato e testes antes de gravar JSON paralelo.

## Motores e decisões existentes

- FFmpeg/FFprobe: continua sendo camada canônica de mídia.
- HyperFrames 0.7.82: motor de motion ativo aprovado em ADR-0003, com versão fixada no projeto.
- Remotion: candidato para experimento comparativo isolado. A instalação e utilização institucional dependem de avaliação de licença e de um novo ADR aprovado que defina como conviverá com HyperFrames; não adicionar ao package.json principal por padrão.
- Plugins do Claude: instruções para o agente, não substituição do runtime local nem dos gates do repositório.

Evitar dois motores ativos no mesmo job. Um piloto comparativo pode usar branches/pastas isoladas sem modificar o lockfile principal; resultados devem ser medidos com o mesmo storyboard e os mesmos assets aprovados.

## Organização da produção

- config/editorials/inova-explica.yaml: configurações existentes, não adicionar campos sem validar schema/consumidores.
- .claude/skills: especializações editoriais e visuais para Claude Code.
- .agents/skills: especializações já existentes do Codex; não duplicar contratos.
- docs/implementation/inova-explica-pilot-01.md: especificação do primeiro piloto.
- workspace/: originais, intermediários, renders e evidências sensíveis, sempre ignorados pelo Git.
- assets/registry.yaml: única lista canônica dos ativos homologados.

## Gates atuais

DESIGN.md ainda declara pendências de tipografia, line art, safe areas, motion tokens e aprovação institucional. Até que sejam resolvidas, o trabalho autorizado neste ramo é documentação, desenho e skills — não produção de um master institucional.

Para habilitar os renders futuros:
1. Registrar fontes, licenças, áreas seguras e tokens.
2. Revisar e aprovar os hero frames propostos.
3. Registrar aprovação humana e atualizar o gate conforme governança existente.
4. Só então compor, executar QA e emitir drafts.
5. Render final apenas com approval.json válido; publicação exige autorização adicional.

## Definição de sucesso

Uma peça Inova Explica só será classificada como profissional quando cumprir conjuntamente: clareza do tema, roteiro factual, motion com função, legibilidade em smartphone, domínio técnico verificado, identidade aprovada e revisão humana. Um build sem erros não é evidência suficiente.

## Evidência e mudanças

Cada PR deve registrar arquivos alterados, testes executados, resultados efetivos, gates ainda fechados e limitações. Nunca reportar teste de render que não ocorreu.
