# Tabela de Decisao do Escopo

| Regra | Projeto selecionado | Branch | MR | Commit | Acao |
| --- | --- | --- | --- | --- | --- |
| R1 | nao | qualquer | qualquer | qualquer | erro de entrada |
| R2 | sim | N/A | N/A | N/A | erro de escopo |
| R3 | sim | selecionado | N/A | N/A | processar branch |
| R4 | sim | selecionado | N/A | selecionado | processar commit |
| R5 | sim | N/A | selecionado | N/A | processar MR |
| R6 | sim | selecionado | selecionado | qualquer | erro de escopo ambiguo |

## Evidencia automatizada

- R3: `tests/test_acceptance.py::test_acceptance_estimar_tamanho_funcional_por_branch`
- R4: `tests/test_fp_service.py::test_process_commit_uses_parent_diff`
- R5: `tests/test_fp_service.py::test_process_merge_request_uses_resolved_shas_for_compare_and_file_read`
- Regras de contrato do processamento: `tests/test_fp_service.py::test_process_fp_count_requires_target_branch_when_compare_is_true`
