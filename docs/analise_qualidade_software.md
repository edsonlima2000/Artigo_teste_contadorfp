# Documentação Técnica de Qualidade de Software

## 1. Descrição do sistema e funcionalidades

O sistema é um **contador assistido de Pontos de Função (SFP)** para projetos GitLab, com interface gráfica em Tkinter e suporte a análise via Azure OpenAI.

### Objetivo funcional
- Permitir a seleção de um projeto GitLab e, opcionalmente, de issue, branch, merge request e commit.
- Coletar arquivos de código (por extensão suportada), montar uma descrição contextual e consultar um modelo de IA para estimar Pontos de Função.
- Exibir o total de SFP e os elementos detalhados por arquivo em uma grade da interface.

### Fluxos suportados
- **Fluxo por Merge Request:** compara `source_branch` com `target_branch` e analisa arquivos alterados.
- **Fluxo por Branch (sem commit):** analisa os arquivos do branch inteiro.
- **Fluxo por Branch + Commit:** calcula mudanças relacionadas ao commit selecionado em relação ao commit anterior.

### Dependências externas críticas
- **GitLab API** (projetos, issues, branches, merge requests, commits, conteúdo de arquivos e comparações).
- **Azure OpenAI** para inferência da contagem de pontos.
- **Arquivo `prompt.txt`** com template da instrução enviada ao modelo.
- **Variáveis de ambiente (.env)** para autenticação e parâmetros de retry/chunking.

---

## 2. Principais módulos e responsabilidades

## 2.1 `ContadorSFP.py` (módulo principal)
Responsável por toda a orquestração do sistema:
- Configuração de ambiente, logging e clientes de integração.
- Coleta de dados no GitLab.
- Regras de seleção na UI (comboboxes e validações).
- Processamento de escopo (branch, MR, commit).
- Preparação de insumo para IA e agregação de resultados.
- Renderização da saída na grade.

### Subconjuntos lógicos internos
1. **Integrações e configuração:** `load_dotenv`, cliente GitLab, configuração OpenAI.
2. **Consulta de artefatos GitLab:** `get_projects`, `get_issues`, `get_branches`, `get_merge_requests`, `get_commits`.
3. **Eventos de UI:** `update_issues`, `update_branches_mrs`, `update_commits_branch`, `update_commits_mr`, `process_selection`.
4. **Processamento de SFP:** `process_fp_count`, `process_fp_count_commit`.
5. **Utilidades de suporte:** `get_previous_commit`, `get_diff_between_commits`, `ler_arquivos_codigo`, `gerar_descricao_projeto`, `gerar_descricao_detalhada`, `consultar_especialista_ai`, `preencher_grid`.

## 2.2 `teste_conexao_OpenAiClientAzure.py` (script auxiliar)
Script de smoke test para validar autenticação e conectividade com Azure OpenAI, enviando uma solicitação simples de chat completion.

---

## 3. Contratos de qualidade por função principal

> Convenção: 
> - **Pré-condições:** condições necessárias antes da execução.
> - **Pós-condições:** garantias esperadas após execução sem erro.
> - **Invariantes:** propriedades que devem permanecer verdadeiras durante o ciclo de vida/função.

## 3.1 Funções de consulta GitLab

### `get_projects()`
- **Pré-condições**
  - Cliente `gl` autenticado e endpoint acessível.
- **Pós-condições**
  - Retorna lista de projetos do usuário proprietário.
- **Invariantes**
  - Não altera estado da UI diretamente.

### `get_issues(project)`
- **Pré-condições**
  - `project` válido obtido da API.
- **Pós-condições**
  - Retorna lista iniciada por `"N/A"` e demais itens no formato `"iid: título"`.
- **Invariantes**
  - O índice 0 sempre representa opção nula (`"N/A"`).

### `get_branches(project, jira_key=None)`
- **Pré-condições**
  - `project` válido.
  - Se `jira_key` informado, deve ser string comparável em lowercase.
- **Pós-condições**
  - Lista de branches filtrada por `jira_key` (quando houver), com `"N/A"` no início.
- **Invariantes**
  - Não retorna branches com transformação de nome (mantém branch original).

### `get_merge_requests(project, jira_key=None)`
- **Pré-condições**
  - `project` válido.
- **Pós-condições**
  - Lista de MRs no formato `"iid: título"` com opção inicial `"N/A"`.
- **Invariantes**
  - Se `jira_key` for usado, o filtro ocorre sobre título do MR.

### `get_commits(project, branch_name=None, mr_iid=None, jira_key=None)`
- **Pré-condições**
  - `project` válido.
  - No máximo um contexto entre `branch_name` e `mr_iid` deve ser considerado por chamada.
- **Pós-condições**
  - Retorna lista iniciada por `"N/A"` com itens `"short_id: título"`.
  - Atualiza `commit_map[short_id] = commit.id` para commits retornados.
- **Invariantes**
  - `commit_map` deve manter mapeamento consistente para commits presentes na lista exibida.

## 3.2 Funções de evento/seleção de UI

### `update_issues(*args)`
- **Pré-condições**
  - `project_var` contém `"id: nome"` válido.
- **Pós-condições**
  - Recarrega issues e branches; limpa MR/commit para `"N/A"`.
- **Invariantes**
  - Mudança de projeto invalida seleções dependentes anteriores.

### `update_branches_mrs(*args)`
- **Pré-condições**
  - Projeto válido selecionado.
- **Pós-condições**
  - Atualiza branches, MRs e commits possivelmente filtrados por chave de issue.
- **Invariantes**
  - Seleções dependentes são resetadas para evitar estado incoerente.

### `update_commits_branch(*args)`
- **Pré-condições**
  - `branch_var != "N/A"`.
- **Pós-condições**
  - MR é resetado para `"N/A"`; commits são recarregados para o branch.
- **Invariantes**
  - Seleção de branch e MR não coexistem como seleção ativa.

### `update_commits_mr(*args)`
- **Pré-condições**
  - `merge_request_var != "N/A"`.
- **Pós-condições**
  - Branch/commit são resetados e commits do MR são obtidos.
- **Invariantes**
  - Prioridade de contexto do MR sobre branch na UI.

### `process_selection()`
- **Pré-condições**
  - Projeto selecionado.
  - Regra de exclusão mútua entre branch e MR respeitada.
- **Pós-condições**
  - Dispara exatamente um fluxo de processamento válido (MR, branch, branch+commit).
  - Atualiza `output_label` com total ou erro.
- **Invariantes**
  - Metadados de execução (timestamp + filtros) são propagados para a rotina de cálculo.

## 3.3 Funções de processamento principal

### `process_fp_count(project, source_branch, target_branch=None, compare=True, metadata_info=None)`
- **Pré-condições**
  - `project` válido.
  - `source_branch` acessível.
  - Se `compare=True`, `target_branch` deve ser informado e comparável.
- **Pós-condições**
  - Retorna inteiro/numérico agregado de `Total_SFP`.
  - Escreve resultados intermediários em `resultado_intermediario.txt`.
  - Atualiza a grid com `Elementos_FP`.
- **Invariantes**
  - Apenas arquivos com extensões suportadas entram no cálculo.
  - `resultado_total['Total_SFP']` é soma acumulada das respostas válidas da IA.

### `process_fp_count_commit(project, selected_commit_id, metadata_info=None)`
- **Pré-condições**
  - `selected_commit_id` existente.
  - Existe commit anterior para comparação (ou fluxo trata ausência).
- **Pós-condições**
  - Analisa diffs entre commit atual e anterior.
  - Atualiza grid e retorna total agregado.
- **Invariantes**
  - Mesmo critério de extensão suportada da análise por branch/MR.

## 3.4 Funções de apoio

### `get_previous_commit(project, commit_id)`
- **Pré-condições**
  - `commit_id` pertence à lista de commits do branch usado pela função.
- **Pós-condições**
  - Retorna commit imediatamente anterior na lista ou `None`.
- **Invariantes**
  - Não altera histórico remoto; apenas leitura.

### `get_diff_between_commits(project, from_commit_id, to_commit_id)`
- **Pré-condições**
  - IDs de commit válidos.
- **Pós-condições**
  - Retorna estrutura de diffs da API.
- **Invariantes**
  - Operação determinística para mesmo par de commits.

### `ler_arquivos_codigo(files, project)`
- **Pré-condições**
  - Lista de arquivos com `path` e `type`.
- **Pós-condições**
  - Retorna dicionário `{path: conteudo}` apenas para blobs com extensões suportadas.
- **Invariantes**
  - Arquivos inválidos ou inacessíveis não interrompem processamento global.

### `gerar_descricao_projeto(files)`
- **Pré-condições**
  - Estrutura de arquivos com campos mínimos esperados.
- **Pós-condições**
  - Retorna string textual com componentes encontrados.
- **Invariantes**
  - Sempre retorna uma string não vazia com cabeçalho.

### `gerar_descricao_detalhada(conteudo_arquivos)`
- **Pré-condições**
  - `conteudo_arquivos` em formato de dicionário.
- **Pós-condições**
  - Retorna string concatenada com conteúdo por arquivo.
- **Invariantes**
  - Preserva associação entre path e conteúdo.

### `consultar_especialista_ai(descricao_projeto, descricao_detalhada, caminho_arquivo)`
- **Pré-condições**
  - `prompt.txt` existente e legível.
  - Credenciais OpenAI válidas.
  - Resposta esperada em JSON parseável.
- **Pós-condições**
  - Retorna dicionário com chaves `Total_SFP` e `Elementos_FP` (agregadas por blocos).
- **Invariantes**
  - Chunking respeita `AZURE_OPENAI_TAMANHO_BLOCO`.
  - Tentativas respeitam `MAX_RETRIES` e `RETRY_DELAY`.

### `preencher_grid(elementos_fp)`
- **Pré-condições**
  - Estrutura dos elementos compatível com a grade.
- **Pós-condições**
  - Grid é limpa e preenchida com dados atualizados.
- **Invariantes**
  - Cada linha inserida contém 4 colunas (`Nome_Arquivo`, `Extensao`, `Elemento_FP`, `Pontos`).

---

## 4. Propriedades relevantes para testes de qualidade

## 4.1 Robustez funcional
- **Exclusão mútua branch vs MR:** nunca processar ambos na mesma execução.
- **Filtro de extensão:** arquivos fora da whitelist não podem contribuir para `Total_SFP`.
- **Integridade de mapeamento de commits:** `commit_map` deve conter todos os commits exibidos para seleção.
- **Resiliência a falhas da API GitLab/OpenAI:** erro em um arquivo não deve interromper lote inteiro.

## 4.2 Corretude de agregação
- **Aditividade de `Total_SFP`:** total final deve ser soma de subtotais válidos retornados por arquivo/bloco.
- **Sincronia resultado/grade:** número e conteúdo dos `Elementos_FP` devem refletir o resultado agregado.
- **Persistência de metadados:** `Metadata` precisa conter os filtros da execução.

## 4.3 Qualidade de integração
- **Contrato de resposta da IA:** resposta deve ser JSON válido com schema mínimo esperado.
- **Determinismo parcial:** com mesma entrada e resposta mockada da IA, saída deve ser idêntica.
- **Tempo de recuperação:** em erro transitório, retries devem ocorrer com delay configurado.

## 4.4 Segurança e confiabilidade
- **Ausência de segredos hardcoded:** credenciais devem vir do `.env`.
- **Tratamento de entradas vazias/N/A:** não gerar exceções por seleção incompleta.
- **Confiabilidade de parsing de seleção UI:** strings `"id: nome"` devem ser parseadas sem perda de integridade.

---

## 5. Sugestão de casos de teste

## 5.1 Testes unitários (com mocks)
1. **`get_commits` por branch**
   - Mock de API retorna 3 commits; verificar lista com `"N/A"` + 3 itens e `commit_map` preenchido.
2. **`get_commits` por MR**
   - Mock de MR com commits; validar uso de `mr.commits()`.
3. **`update_commits_branch`**
   - Dado branch selecionado, deve resetar MR/commit e recarregar commits.
4. **`update_commits_mr`**
   - Dado MR selecionado, deve resetar branch/commit e bloquear seleção de commit (lista `"N/A"`).
5. **`gerar_descricao_projeto`**
   - Com e sem arquivos elegíveis; validar textos esperados.
6. **`consultar_especialista_ai` com chunking**
   - Forçar tamanho pequeno de bloco e mockar duas respostas JSON; validar soma agregada.
7. **`preencher_grid`**
   - Dados com/sem `Extensao`; verificar derivação por `os.path.splitext`.

## 5.2 Testes de integração
1. **Fluxo branch completo (sem commit)**
   - Projeto/branch válidos, comparar total e linhas da grade.
2. **Fluxo branch + commit**
   - Commit com commit anterior; validar que apenas diffs entram no cálculo.
3. **Fluxo MR**
   - MR com source/target; validar chamada a `repository_compare` e cálculo por arquivos alterados.
4. **Falha parcial de arquivos**
   - Simular erro em leitura de 1 arquivo e sucesso nos demais; processamento deve concluir.
5. **Falha temporária OpenAI**
   - Simular `OpenAIError` nas primeiras tentativas e sucesso depois; validar retry.

## 5.3 Testes de regressão recomendados
- Seleção inválida de projeto/branch/MR deve exibir mensagem amigável em `output_label`.
- Alterações na estrutura do JSON retornado pela IA devem ser capturadas por teste de contrato.
- Mudanças na whitelist de extensões devem ser cobertas por testes parametrizados.

---

## 6. Riscos técnicos observados e melhorias de qualidade

- **Acoplamento elevado no módulo único (`ContadorSFP.py`):** UI, domínio e integração estão misturados.
  - *Melhoria:* separar em camadas (`ui.py`, `services/gitlab_service.py`, `services/ai_service.py`, `domain/fp_counter.py`).
- **Dependência forte de formato textual da UI (`"id: título"`):** parsing frágil.
  - *Melhoria:* armazenar objetos/IDs em estrutura dedicada em vez de parsing de string.
- **Tratamento de exceções heterogêneo:** alguns pontos logam, outros só imprimem.
  - *Melhoria:* padronizar observabilidade (logging estruturado + códigos de erro).
- **Side effects na importação do módulo principal:** inicializa UI e integrações ao importar.
  - *Melhoria:* encapsular boot em `main()` e usar `if __name__ == "__main__":`.
- **Testabilidade limitada por dependências globais (`gl`, variáveis Tkinter, `commit_map`).**
  - *Melhoria:* injeção de dependências e redução de estado global.

---

## 7. Estratégia de qualidade recomendada (próximos passos)

1. **Curto prazo (rápido ganho):**
   - Criar testes unitários com `pytest` + `unittest.mock` para funções de transformação e seleção.
   - Adicionar validações explícitas de pré-condição com mensagens de erro padronizadas.

2. **Médio prazo:**
   - Refatorar para arquitetura em camadas e aumentar cobertura de integração com mocks de GitLab/OpenAI.
   - Introduzir tipagem (`typing`) e checagem estática (`mypy/pyright`).

3. **Longo prazo:**
   - Adotar testes baseados em propriedades (Hypothesis) para entradas de diffs/respostas da IA.
   - Criar pipeline CI com gates de qualidade (lint, testes, cobertura, análise estática).

---

## 8. Localização do artefato de documentação

- **Caminho relativo no repositório:** `docs/analise_qualidade_software.md`
- **URL local completa (ambiente atual):** `file:///workspace/Contador_FP_RDSaude/docs/analise_qualidade_software.md`

> Observação: a URL HTTP(S) pública depende do remote configurado (GitHub/GitLab) e do branch publicado.
