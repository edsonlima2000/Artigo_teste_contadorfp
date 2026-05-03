# Contratos do SUT

## FunctionPointService.process_fp_count

Pre-condicoes:

- `project` obrigatorio.
- `source_branch` obrigatorio.
- `target_branch` obrigatorio quando `compare=True`.

Pos-condicoes:

- Retorna dicionario com `Total_SFP` e `Elementos_FP`.
- Arquivos inelegiveis nao contribuem para o total.
- Arquivos com erro de leitura sao ignorados sem interromper todo o lote.
- Leituras por branch/MR usam SHA resolvido no inicio do processamento.

## FunctionPointService.process_fp_count_commit

Pre-condicoes:

- `project` obrigatorio.
- `selected_commit_id` obrigatorio.

Pos-condicoes:

- Usa parent do commit quando disponivel.
- Processa diff do commit quando nao ha parent.
- Retorna total agregado.

## AzureOpenAIAnalyzer.consultar_especialista_ai

Pre-condicoes:

- `descricao_projeto` obrigatoria.
- `descricao_detalhada` obrigatoria.
- `caminho_arquivo` obrigatorio.
- `prompt.txt` existente.
- Parametros de bloco/retry validos.

Pos-condicoes:

- Retorna JSON agregado com `Total_SFP` numerico e `Elementos_FP` lista.
- Aceita JSON puro ou JSON envelopado em markdown.
- Rejeita schema invalido.

## GitLabService.get_commits

Pos-condicoes:

- Retorna lista iniciada por `N/A`.
- Preenche `commit_map` com `short_id -> commit.id`.
