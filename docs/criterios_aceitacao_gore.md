# Criterios de Aceitacao Orientados a Metas

## Meta G1: Estimar tamanho funcional do repositorio

Cenario:

- Dado um projeto GitLab valido.
- E um branch valido com arquivo elegivel.
- Quando o processamento por branch e executado.
- Entao o sistema retorna `Total_SFP` e `Elementos_FP`.

Evidencia:

- `tests/test_acceptance.py::test_acceptance_estimar_tamanho_funcional_por_branch`

## Meta G2: Ignorar artefatos sem relevancia funcional

Cenario:

- Dado um escopo contendo apenas arquivos inelegiveis.
- Quando o processamento e executado.
- Entao o sistema nao chama a IA.
- E o total retornado e zero.

Evidencia:

- `tests/test_acceptance.py::test_acceptance_ignorar_arquivos_inelegiveis`

## Meta G3: Manter consistencia temporal do escopo

Cenario:

- Dado um branch selecionado.
- Quando o processamento e iniciado.
- Entao o sistema resolve o SHA do branch.
- E usa esse SHA nas leituras dos arquivos.

Evidencia:

- `tests/test_fp_service.py::test_process_branch_filters_files_and_reads_by_resolved_sha`
- `tests/test_fp_service.py::test_process_merge_request_uses_resolved_shas_for_compare_and_file_read`
