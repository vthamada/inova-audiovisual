# Solução de problemas

## `npx.ps1` ou `npm.ps1` bloqueado

Use `npx.cmd` ou `npm.cmd`. Não altere a Execution Policy do sistema apenas para o projeto.

Os entrypoints oficiais deste repositório são `scripts/doctor.cmd`, `scripts/verify.cmd` e `scripts/npm-project.cmd`. Os arquivos `.ps1` são opcionais e só funcionam quando a política local já os permite.

## Node incompatível

`doctor` exige Node 24. O Node 25.9.0 existente está EOL. Execute a distribuição isolada em `.tools` ou ative Node 24 por um gerenciador aprovado.

## Mais de um FFmpeg

Use o caminho mostrado pelo `doctor`. Não conclua que um codec está disponível porque outra build no `PATH` o lista. Ajuste `config/pipeline.yaml` para o caminho aprovado.

## HyperFrames sem browser

Execute com o npm do runtime Node 24:

```powershell
.\scripts\npm-project.cmd run browser:ensure
.\scripts\npm-project.cmd run doctor
```

Chrome comum e Edge não substituem automaticamente o Chrome Headless Shell gerenciado pelo HyperFrames.

## Whisper falha ao imprimir ajuda

O CLI global do OpenAI Whisper encontrou erro de CP1252 neste host. Para diagnóstico manual, use UTF-8:

```powershell
$env:PYTHONUTF8 = "1"
whisper --help
```

Essa instalação global não é o provider oficial do projeto.

## Schema inválido

Execute:

```powershell
.\.venv\Scripts\inova-av.exe schema validate project caminho\project.yaml
```

O erro mostra o caminho do campo. Erro semântico pode ocorrer mesmo quando o JSON Schema estrutural passa, por exemplo segmentos sobrepostos ou `out <= in`.

## Render final bloqueado

O bloqueio é esperado se estado, autorização, revisão jurídica, revisor ou hash não coincidir. Não edite o YAML para contornar o gate e não crie opção `--force`.
