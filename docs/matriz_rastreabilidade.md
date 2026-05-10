# Matriz de Rastreabilidade

| Tecnica | Elemento do artigo | Implementacao | Evidencia de teste |
| --- | --- | --- | --- |
| MDE | Blocos de extensao elegivel | `descriptions.is_supported_path` | `tests/test_descriptions.py::test_is_supported_path_accepts_code_extensions` |
| MDE | Blocos de extensao inelegivel | `descriptions.is_supported_path` | `tests/test_descriptions.py::test_is_supported_path_rejects_non_code_extensions` |
| MDE | Descricao considera apenas arquivos elegiveis | `gerar_descricao_projeto` | `tests/test_descriptions.py::test_gerar_descricao_projeto_keeps_only_supported_files` |
| MDE | Preservacao de path e conteudo | `gerar_descricao_detalhada` | `tests/test_descriptions.py::test_gerar_descricao_detalhada_preserves_path_and_content` |
| CCE | Cada tipo de escopo relevante aparece em teste | `FunctionPointService` | Branch: `tests/test_fp_service.py::test_process_branch_filters_files_and_reads_by_resolved_sha`; MR: `tests/test_fp_service.py::test_process_merge_request_uses_resolved_shas_for_compare_and_file_read`; Commit: `tests/test_fp_service.py::test_process_commit_uses_parent_diff` |
| CEB | Cenario base valido com variacoes controladas | `FunctionPointService` + fakes | Base por branch: `tests/test_acceptance.py::test_acceptance_estimar_tamanho_funcional_por_branch`; variacao com inelegiveis: `tests/test_acceptance.py::test_acceptance_ignorar_arquivos_inelegiveis` |
| Contratos | Pre-condicoes de processamento | `require` em `FunctionPointService` | `tests/test_fp_service.py::test_process_fp_count_requires_target_branch_when_compare_is_true` |
| Contratos | Pos-condicoes de processamento | `ensure` + `validate_fp_result` | `tests/test_contracts.py::test_ensure_materializes_postcondition`; `tests/test_contracts.py::test_validate_fp_result_rejects_invalid_postcondition` |
| Contratos | Invariantes de processamento | `invariant` + `validate_processing_invariants` | `tests/test_contracts.py::test_invariant_materializes_processing_invariant`; `tests/test_contracts.py::test_validate_processing_invariants_rejects_invalid_state` |
| Contratos | Schema da resposta da IA | `validate_ai_response` | `tests/test_ai_client.py::test_ai_client_rejects_invalid_schema` |
| Contratos | JSON puro valido da IA | `AzureOpenAIAnalyzer.consultar_especialista_ai` | `tests/test_ai_client.py::test_ai_client_parses_json_response` |
| Contratos | JSON em markdown valido da IA | `AzureOpenAIAnalyzer.consultar_especialista_ai` | `tests/test_ai_client.py::test_ai_client_parses_markdown_json_response` |
| MBT | Decisao por branch | `FunctionPointService.process_fp_count(compare=False)` | `tests/test_fp_service.py::test_process_branch_filters_files_and_reads_by_resolved_sha` |
| MBT | Decisao por MR | `FunctionPointService.process_fp_count(compare=True)` | `tests/test_fp_service.py::test_process_merge_request_uses_resolved_shas_for_compare_and_file_read` |
| MBT | Decisao por commit | `FunctionPointService.process_fp_count_commit` | `tests/test_fp_service.py::test_process_commit_uses_parent_diff` |
| MBT | Caminhos de estado do processamento | `FunctionPointService` | Modelo documentado em `docs/maquina_estados_processamento.md`; exercitado por `tests/test_fp_service.py` e `tests/test_acceptance.py` |
| GORE | Meta: estimar tamanho funcional | `FunctionPointService.process_fp_count` | `tests/test_acceptance.py::test_acceptance_estimar_tamanho_funcional_por_branch` |
| GORE | Meta: ignorar artefatos inelegiveis | `is_supported_path` + `FunctionPointService` | `tests/test_acceptance.py::test_acceptance_ignorar_arquivos_inelegiveis` |
| Invariante | Resolver branch para SHA | `GitLabService.resolve_branch_sha` | `tests/test_gitlab_service.py::test_resolve_branch_sha_returns_branch_commit_id` |
| Invariante | Ler arquivos por SHA no fluxo branch | `FunctionPointService._process_branch` | `tests/test_fp_service.py::test_process_branch_filters_files_and_reads_by_resolved_sha` |
| Invariante | Ler arquivos por SHA no fluxo MR | `FunctionPointService._process_branch_comparison` | `tests/test_fp_service.py::test_process_merge_request_uses_resolved_shas_for_compare_and_file_read` |
| GitLab fake | Mapeamento de commits | `GitLabService.get_commits` | `tests/test_gitlab_service.py::test_get_commits_populates_commit_map` |
| GitLab fake | Commit anterior por parent | `GitLabService.get_previous_commit` | `tests/test_gitlab_service.py::test_get_previous_commit_uses_parent_id_first` |
