# Escopo do MVP

## Objetivo

Produzir, a partir de um vídeo compatível com uma pessoa falando, um Reel preliminar 1080 × 1920, legendado, com identidade oficial, áudio inteligível, relatório de revisão e rastreabilidade completa. A versão final só pode ser gerada após aprovação humana válida.

## Caso de uso de referência

- uma câmera;
- uma pessoa principal;
- fala em português brasileiro;
- áudio embutido;
- duração curta ou média;
- destino inicial Instagram Reels;
- corte de até 60 segundos configurável;
- acabamento institucional simples.

Entrevista com entrevistador fora de quadro pode ser aceita se não exigir diarização ou multicâmera. Casos com várias vozes relevantes são encaminhados para revisão/manual ou quarentena de escopo.

## Incluído

1. Ingestão local de um arquivo.
2. Nome interno seguro, cópia imutável e SHA-256.
3. FFprobe de codec, streams, resolução, frame rate, duração e áudio.
4. Validação e quarentena com erro acionável.
5. Proxy de trabalho.
6. Extração WAV.
7. Transcrição pt-BR por provider local.
8. Timestamps por segmento e, quando suportado, por palavra.
9. TXT, JSON, SRT e VTT revisáveis.
10. Detecção de silêncio.
11. Sugestões de trechos, ganchos e riscos, sem reescrever fala.
12. Edit plan rastreável.
13. Primeiro corte.
14. Adaptação 1080 × 1920 com estratégia inicial de crop/pad.
15. Área segura configurável e verificação visual.
16. Legenda ASS incorporada, além de arquivo separado.
17. Logo de canto, lower third e encerramento oficiais.
18. Normalização de áudio; trilha licenciada é opcional e desligada por padrão.
19. Preview de qualidade draft.
20. Relatório e checklist de revisão.
21. Alterações versionadas e novo preview.
22. Gate de aprovação vinculado a hashes.
23. Render final e clean master.
24. Manifesto e pacote final.

## Não incluído

- publicação automática;
- painel web ou app;
- filas e n8n;
- sync com Drive/WordPress;
- multicâmera;
- diarização como requisito;
- B-roll automático;
- busca na internet;
- mídia sintética;
- clonagem de voz;
- TTS;
- MusicGen;
- remoção complexa de fundo;
- face tracking avançado;
- máscaras quadro a quadro;
- exportação NLE completa;
- processamento distribuído;
- múltiplos usuários e permissões complexas.

## Critérios de entrada

Proposta inicial, a validar com fixtures:

- container MP4 ou MOV;
- vídeo H.264/HEVC/ProRes decodificável pela build fixada;
- ao menos uma faixa de áudio decodificável;
- duração máxima configurável, inicialmente 30 minutos por job;
- arquivo dentro do limite de disco reservado;
- caminho e nome seguros;
- autorização de imagem registrada como `pending`, `approved`, `denied` ou `not_required`.

Arquivo fora desses critérios recebe explicação e pode ir para quarentena; nunca é alterado no lugar.

## Critérios de aceite funcional

O MVP passa quando uma fixture e ao menos um material real autorizado:

- percorrem `received` até `under_review`;
- geram todos os artefatos esperados com schemas válidos;
- mantêm a duração e os timecodes dentro da origem;
- produzem SRT e ASS sincronizados;
- produzem preview 1080 × 1920 com vídeo e áudio;
- exibem logo/lower third/encerramento aprovados;
- passam por checklist visual e de áudio;
- bloqueiam render final sem aprovação;
- invalidam aprovação após mudança de artefato;
- geram final somente com todos os gates válidos;
- funcionam com caminhos contendo espaços;
- funcionam offline após provisionamento.

## Critérios não funcionais

- logs estruturados e legíveis;
- retomada após falha;
- configuração fora do código;
- execução determinística dentro de tolerâncias declaradas;
- testes unitários e integração no Windows;
- nenhuma credencial ou mídia no Git;
- comandos sem shell injection;
- versões de ferramentas no manifesto;
- preview antes de render final;
- erros específicos, sem sucesso falso.

## Qualidade editorial e visual

Revisão manual confirma:

- fidelidade da fala;
- contexto suficiente;
- nomes e cargos;
- sincronização e quebras semânticas;
- no máximo duas linhas de legenda;
- contraste;
- rosto não coberto;
- área segura para interface da plataforma;
- áudio inteligível;
- música abaixo da voz, quando houver;
- uso correto dos assets;
- ausência de personalismo indevido.

## Estratégia de enquadramento do MVP

Começar com regras determinísticas:

1. usar crop central quando a pessoa já está na região segura;
2. permitir ponto focal manual no `project.yaml`;
3. usar pad/blur aprovado quando o crop destruir contexto;
4. tratar rastreamento facial automático como experimento posterior.

O MVP não promete reenquadramento automático perfeito. O preview sempre mostra guias de área segura durante a revisão.

## Transcrição

Provider proposto: `faster-whisper` em CPU `int8`, com modelo `small` como baseline e `medium` como candidato de qualidade. A escolha final depende de benchmark pt-BR com material autorizado. O `openai-whisper medium` já instalado serve como comparador, não como dependência do projeto.

Referências técnicas:

- <https://github.com/SYSTRAN/faster-whisper>
- <https://github.com/openai/whisper>
- <https://github.com/ggml-org/whisper.cpp>

## Medições necessárias

Não há estimativa honesta de tempo ou armazenamento sem material. A Fase 1/validação deverá medir:

- tempo real de transcrição por minuto;
- pico de RAM;
- tempo de preview e render final;
- tamanho de original, proxy, WAV, frames/cache e saídas por minuto;
- ganho de Quick Sync versus `libx264`;
- precisão de palavras críticas em pt-BR;
- legibilidade em aparelhos reais.

Relatórios usarão faixas observadas e configuração do teste, nunca promessa genérica.

## Definição de concluído

O MVP só será concluído quando código, schemas, testes, golden fixture, documentação operacional e validação humana em material real autorizado existirem. Build, lint ou render sintético isolado não provam qualidade institucional.
