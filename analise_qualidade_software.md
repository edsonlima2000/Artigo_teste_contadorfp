# Especificacao Tecnica do Projeto

## 1. Contexto academico

Este projeto e o Sistema Sob Teste (SUT) utilizado em um artigo academico de
Mestrado em Computacao Aplicada, na disciplina de Qualidade e Teste de Software.
O SUT e um Contador Automatizado de Pontos de Funcao (SFP) desenvolvido em
Python para estimar impacto funcional de alteracoes em repositorios GitLab com
apoio de Azure OpenAI.

No artigo, o sistema e usado como base pratica para discutir e aplicar tecnicas
de verificacao e validacao:

- Modelagem do Dominio da Entrada (MDE), com Cobertura de Cada Escolha (CCE) e
  Escolha da Base (CEB).
- Teste Baseado em Contratos, com pre-condicoes, pos-condicoes e invariantes.
- Teste Baseado em Modelos (MBT), com tabelas de decisao e maquinas de estados.
- Teste de Aceitacao orientado a metas de negocio (GORE).

O foco academico recai sobre o modulo de processamento da contagem funcional:
definicao do escopo de analise, recuperacao de artefatos do GitLab, filtro de
arquivos elegiveis, envio de contexto ao especialista de IA e consolidacao do
total de SFP.

## 2. Objetivo do sistema

O objetivo funcional do sistema e automatizar parte do processo de estimativa de
Pontos de Funcao a partir de alteracoes de codigo controladas no GitLab.

O sistema deve:

- Listar projetos GitLab acessiveis ao token configurado.
- Permitir a selecao de issue, branch, merge request ou commit.
- Recuperar arquivos do escopo escolhido.
- Filtrar arquivos por extensoes de codigo suportadas.
- Montar descricoes textuais estruturadas para analise.
- Enviar essas descricoes ao Azure OpenAI usando o template `prompt.txt`.
- Receber uma resposta JSON com `Total_SFP` e `Elementos_FP`.
- Consolidar o total e exibir os elementos funcionais em uma grade Tkinter.
- Registrar resultados intermediarios em `resultado_intermediario.txt`.

## 3. Escopo funcional

### 3.1 Fluxo por branch

Entrada principal: projeto GitLab e branch.

Comportamento esperado:

1. O sistema recupera a arvore completa do branch.
2. Cada arquivo e avaliado pelo filtro de extensoes suportadas.
3. Arquivos elegiveis sao lidos no proprio branch selecionado.
4. Cada arquivo elegivel gera uma descricao detalhada.
5. A descricao e enviada ao Azure OpenAI.
6. As respostas validas sao agregadas em um resultado total.

Saida esperada:

- `Total_SFP` numerico.
- Lista de `Elementos_FP`.
- Grade de interface preenchida.
- Registro textual no arquivo intermediario.

### 3.2 Fluxo por merge request

Entrada principal: projeto GitLab e merge request.

Comportamento esperado:

1. O sistema identifica `source_branch` e `target_branch` do MR.
2. O sistema executa comparacao entre os branches.
3. Apenas arquivos alterados no diff entram no processamento.
4. Arquivos fora da lista de extensoes suportadas sao ignorados.
5. Arquivos elegiveis sao enviados para analise via IA.
6. O resultado final e agregado e exibido.

Regra de consistencia:

- Branch e merge request nao podem ser processados simultaneamente como escopos
  ativos. Ao selecionar MR, a selecao de branch e commit e redefinida.

### 3.3 Fluxo por commit

Entrada principal: projeto GitLab, branch e commit.

Comportamento esperado:

1. O sistema resolve o ID real do commit selecionado a partir do `commit_map`.
2. O sistema busca o commit anterior usando o parent do commit quando disponivel.
3. Se houver commit anterior, calcula o diff entre anterior e atual.
4. Se nao houver parent, usa o diff do proprio commit.
5. Arquivos elegiveis do diff sao processados pela IA.
6. O total de SFP e consolidado.

Racional de qualidade:

- Usar o parent do commit reduz a dependencia de nomes fixos de branch, como
  `master` ou `main`, e fortalece a invariante de consistencia do escopo.

## 4. Arquitetura atual

O projeto foi refatorado para reduzir o acoplamento do script original. O arquivo
`ContadorSFP.py` permanece como ponto de entrada, enquanto a logica principal foi
organizada no pacote `contador_fp`.

Estrutura principal:

```text
ContadorSFP.py
contador_fp/
  __init__.py
  app.py
  ai_client.py
  config.py
  contracts.py
  descriptions.py
  fp_service.py
  gitlab_service.py
prompt.txt
requirements.txt
readme.txt
```

### 4.1 `ContadorSFP.py`

Responsabilidade:

- Servir como ponto de entrada executavel.
- Importar e chamar `contador_fp.app.main()`.

Contrato:

- Nao deve conter regra de negocio.
- Nao deve inicializar dependencias diretamente.
- Deve permanecer simples para facilitar execucao local.

### 4.2 `contador_fp/config.py`

Responsabilidade:

- Carregar variaveis de ambiente com `python-dotenv`.
- Configurar logging em `execucao.log`.
- Configurar o cliente global da biblioteca OpenAI para Azure.
- Criar o cliente GitLab.
- Centralizar constantes do projeto.

Constantes:

- `DEPLOYMENT_NAME = "StudioAI"`
- `SUPPORTED_EXTENSIONS = [".py", ".jsp", ".jspx", ".js", ".ts", ".groovy", ".kt", ".scala"]`

Variaveis de ambiente consumidas:

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `GITLAB_ENDPOINT`
- `GITLAB_PRIVATE_TOKEN`

### 4.3 `contador_fp/gitlab_service.py`

Classe principal: `GitLabService`.

Responsabilidade:

- Encapsular chamadas de leitura ao GitLab.
- Obter projetos, issues, branches, merge requests e commits.
- Manter `commit_map`, associando `short_id` ao ID completo do commit.
- Resolver commit anterior.
- Obter diffs entre commits.

Metodos principais:

- `get_project(project_text)`
- `get_projects()`
- `get_issues(project)`
- `get_branches(project, jira_key=None)`
- `get_merge_requests(project, jira_key=None)`
- `get_commits(project, branch_name=None, mr_iid=None, jira_key=None)`
- `get_previous_commit(project, commit_id)`
- `get_diff_between_commits(project, from_commit_id, to_commit_id)`

Contrato de saida das listas:

- Listas exibidas na UI devem iniciar com `"N/A"`.
- Commits devem ser exibidos no formato `"short_id: titulo"`.
- Merge requests devem ser exibidos no formato `"iid: titulo"`.

### 4.4 `contador_fp/descriptions.py`

Responsabilidade:

- Validar se um caminho de arquivo possui extensao suportada.
- Gerar descricao resumida do projeto/arquivo.
- Gerar descricao detalhada com conteudo do arquivo.

Funcoes:

- `is_supported_path(path)`
- `gerar_descricao_projeto(files)`
- `gerar_descricao_detalhada(conteudo_arquivos)`

Contrato:

- Apenas extensoes definidas em `SUPPORTED_EXTENSIONS` devem ser consideradas
  elegiveis.
- A descricao detalhada deve preservar a relacao entre caminho e conteudo.

### 4.5 `contador_fp/ai_client.py`

Classe principal: `AzureOpenAIAnalyzer`.

Responsabilidade:

- Ler `prompt.txt`.
- Dividir descricoes grandes em blocos.
- Enviar mensagens ao Azure OpenAI.
- Interpretar a resposta como JSON.
- Agregar respostas parciais em um unico resultado.

Variaveis opcionais:

- `AZURE_OPENAI_TAMANHO_BLOCO`, padrao `12000`.
- `AZURE_OPENAI_MAX_RETRIES`, padrao `5`.
- `AZURE_OPENAI_RETRY_DELAY`, padrao `10`.

Contrato de resposta esperado:

```json
{
  "Total_SFP": 0,
  "Elementos_FP": [
    {
      "Nome_Arquivo": "exemplo.py",
      "Extensao": "py",
      "Elemento_FP": "descricao do elemento",
      "Pontos": 0
    }
  ]
}
```

### 4.6 `contador_fp/contracts.py`

Responsabilidade:

- Materializar contratos executaveis do SUT.
- Validar pre-condicoes com `require`.
- Validar pos-condicoes com `ensure` e `validate_fp_result`.
- Validar invariantes de processamento com `invariant` e
  `validate_processing_invariants`.
- Validar o contrato estrutural da resposta da IA com `validate_ai_response`.

### 4.7 `contador_fp/fp_service.py`

Classe principal: `FunctionPointService`.

Responsabilidade:

- Orquestrar a contagem funcional independente da interface.
- Processar branch completo.
- Processar comparacao entre branches.
- Processar commit.
- Agregar respostas da IA.
- Registrar resultados intermediarios.

Metodos publicos:

- `process_fp_count(project, source_branch, target_branch=None, compare=True, metadata_info=None)`
- `process_fp_count_commit(project, selected_commit_id, metadata_info=None)`

Metodos internos relevantes:

- `_process_branch(...)`
- `_process_branch_comparison(...)`
- `_process_diffs(...)`
- `_analyze_file(...)`

Contrato de resultado:

```json
{
  "Total_SFP": 0,
  "Elementos_FP": [],
  "Metadata": {}
}
```

Em caso de erro controlado:

```json
{
  "Total_SFP": 0,
  "Elementos_FP": [],
  "Erro": "mensagem de erro"
}
```

### 4.8 `contador_fp/app.py`

Classe principal: `ContadorSFPApp`.

Responsabilidade:

- Construir a interface Tkinter.
- Carregar projetos na inicializacao.
- Controlar eventos de selecao.
- Validar exclusao mutua entre branch e merge request.
- Acionar `FunctionPointService`.
- Preencher a grade final com `Elementos_FP`.

Componentes de UI:

- Combobox de projeto.
- Combobox de issue.
- Combobox de branch.
- Combobox de merge request.
- Combobox de commit.
- Treeview de resultado com colunas:
  - `Nome_Arquivo`
  - `Extensao`
  - `Elemento_FP`
  - `Pontos`
- Label de saida com total ou erro.

## 5. Contratos de qualidade

### 5.1 Invariantes de sistema

- O escopo ativo deve ser sempre um entre branch, merge request ou branch com
  commit.
- Branch e merge request nao podem permanecer ativos simultaneamente.
- O filtro de extensoes deve ser aplicado antes de qualquer chamada ao Azure
  OpenAI.
- `Total_SFP` deve representar a soma dos totais retornados em respostas validas
  da IA.
- A grade da interface deve refletir os mesmos `Elementos_FP` agregados no
  resultado.
- Credenciais nunca devem estar hardcoded no codigo.
- O arquivo `.env` deve permanecer fora do versionamento.

### 5.2 Pre-condicoes

- O arquivo `.env` deve existir ou as variaveis equivalentes devem estar
  configuradas no ambiente.
- `GITLAB_ENDPOINT` deve apontar para uma instancia GitLab acessivel.
- `GITLAB_PRIVATE_TOKEN` deve possuir permissao de leitura sobre projetos,
  commits, branches, merge requests e arquivos.
- `AZURE_OPENAI_API_KEY` e `AZURE_OPENAI_ENDPOINT` devem ser validos.
- `prompt.txt` deve existir na raiz do projeto.
- O projeto selecionado deve existir no GitLab.
- O branch, MR ou commit selecionado deve pertencer ao projeto.

### 5.3 Pos-condicoes

- Uma execucao bem-sucedida deve retornar `Total_SFP`.
- Arquivos inelegiveis nao devem contribuir para o total.
- Falhas de leitura em um arquivo nao devem interromper todo o lote.
- Falhas controladas devem ser registradas em log ou exibidas ao usuario.
- A interface deve exibir o total geral ao final do processamento.

## 6. Modelo de dominio de entrada

Caracteristicas relevantes:

- Projeto GitLab:
  - existente
  - inexistente/inacessivel
- Escopo:
  - branch
  - merge request
  - branch com commit
  - nenhum escopo selecionado
  - branch e MR selecionados simultaneamente
- Arquivos:
  - lista vazia
  - um arquivo elegivel
  - varios arquivos elegiveis
  - arquivos inelegiveis
  - mistura de elegiveis e inelegiveis
- Resposta da IA:
  - JSON valido
  - JSON envolto em bloco markdown
  - JSON invalido
  - erro transitorio de API
  - erro definitivo de API

Valores limite recomendados:

- Nenhum arquivo elegivel apos filtro.
- Exatamente um arquivo elegivel.
- Descricao com tamanho menor que `AZURE_OPENAI_TAMANHO_BLOCO`.
- Descricao exatamente no limite do bloco.
- Descricao maior que o limite, exigindo multiplos blocos.
- `AZURE_OPENAI_MAX_RETRIES = 1`.
- `AZURE_OPENAI_RETRY_DELAY = 0` em testes automatizados.

## 7. Regras de decisao

Tabela simplificada de selecao de escopo:

| Projeto selecionado | Branch | MR | Commit | Acao esperada |
| --- | --- | --- | --- | --- |
| nao | qualquer | qualquer | qualquer | erro: selecionar projeto |
| sim | N/A | N/A | N/A | erro: selecionar escopo |
| sim | selecionado | N/A | N/A | processar branch |
| sim | selecionado | N/A | selecionado | processar commit |
| sim | N/A | selecionado | N/A | processar MR |
| sim | selecionado | selecionado | qualquer | erro: branch e MR mutuamente exclusivos |

Tabela simplificada de elegibilidade de arquivo:

| Tipo de entrada | Extensao suportada | Acao |
| --- | --- | --- |
| arquivo de codigo | sim | analisar |
| arquivo de codigo | nao | ignorar |
| path vazio | qualquer | ignorar |
| arquivo inacessivel | sim | registrar erro e continuar |

## 8. Modelo de estados

Estados principais:

1. `Inicio`
2. `Ambiente Configurado`
3. `Projeto Selecionado`
4. `Escopo Definido`
5. `Artefatos Recuperados`
6. `Arquivos Filtrados`
7. `Analise em Processamento`
8. `Resultado Gerado`
9. `Erro de Entrada`
10. `Erro de Integracao`

Transicoes principais:

- `Inicio -> Ambiente Configurado`: variaveis carregadas e clientes criados.
- `Ambiente Configurado -> Projeto Selecionado`: usuario escolhe projeto valido.
- `Projeto Selecionado -> Escopo Definido`: usuario escolhe branch, MR ou commit.
- `Escopo Definido -> Artefatos Recuperados`: GitLab retorna arvore ou diff.
- `Artefatos Recuperados -> Arquivos Filtrados`: filtro de extensoes executado.
- `Arquivos Filtrados -> Analise em Processamento`: existe ao menos um arquivo
  elegivel.
- `Analise em Processamento -> Resultado Gerado`: IA retorna JSON valido.
- Qualquer estado de selecao -> `Erro de Entrada`: projeto ou escopo invalido.
- Qualquer estado de integracao -> `Erro de Integracao`: falha GitLab ou Azure
  nao recuperavel.

## 9. Requisitos nao funcionais

### 9.1 Manutenibilidade

- A interface deve permanecer separada da logica de contagem.
- Chamadas GitLab devem ficar encapsuladas em `GitLabService`.
- Chamadas Azure OpenAI devem ficar encapsuladas em `AzureOpenAIAnalyzer`.
- Regras de contagem devem ficar em `FunctionPointService`.

### 9.2 Testabilidade

- Servicos devem receber dependencias por construtor sempre que possivel.
- Chamadas externas devem ser mockaveis em testes unitarios.
- O processamento deve retornar estruturas de dados verificaveis sem depender
  da interface grafica.

### 9.3 Seguranca

- Tokens e chaves devem ser configurados apenas por variaveis de ambiente.
- `.env`, `.venv/`, `venv/`, `__pycache__/` e `*.pyc` devem permanecer ignorados.
- Logs nao devem registrar tokens.

### 9.4 Confiabilidade

- Erros em arquivos individuais nao devem interromper o processamento inteiro.
- Erros transitorios de Azure OpenAI devem respeitar politica de retry.
- O resultado final deve ser consistente com as respostas efetivamente aceitas.

## 10. Plano de testes recomendado

### 10.1 Estrategia de isolamento

A suite de testes implementada usa `pytest` e evita dependencias reais de rede.
Para isso, foram criados fakes de GitLab e Azure OpenAI em `tests/fakes/`.

Os fakes simulam entradas e saidas relevantes para o artigo:

- projetos, branches, commits, merge requests e diffs do GitLab;
- arquivos elegiveis e inelegiveis;
- resposta JSON valida da IA;
- resposta JSON invalida ou com schema invalido.

Essa estrategia permite validar o comportamento do SUT de forma deterministica,
sem depender de token, internet, disponibilidade do GitLab ou variabilidade de
resposta do Azure OpenAI. Do ponto de vista do artigo, isso reforca a
testabilidade e a repetibilidade dos experimentos.

O arquivo `tests/conftest.py` prepara automaticamente cada teste. Ele cria uma
pasta temporaria, adiciona um `prompt.txt` temporario e configura variaveis de
ambiente necessarias para os testes. Assim, a suite nao depende do estado local
real da maquina e nao altera os artefatos de producao do projeto.

A suite e representativa, nao exaustiva. Seu objetivo e demonstrar a aplicacao
das tecnicas do artigo em cenarios selecionados, cobrindo MDE, CCE, CEB,
contratos, MBT, GORE e rastreabilidade.

### 10.2 Testes unitarios

- `is_supported_path`: validar cada extensao suportada e extensoes rejeitadas.
- `gerar_descricao_projeto`: validar entrada com arquivos elegiveis e lista sem
  arquivos elegiveis.
- `gerar_descricao_detalhada`: validar preservacao de path e conteudo.
- `GitLabService.get_commits`: validar preenchimento de `commit_map`.
- `GitLabService.get_previous_commit`: validar uso de parent do commit.
- `AzureOpenAIAnalyzer.consultar_especialista_ai`: validar parsing de JSON puro,
  JSON em markdown, JSON invalido e retry.
- `contracts`: validar pre-condicoes, pos-condicoes, invariantes e schemas
  executaveis.
- `FunctionPointService.process_fp_count`: validar branch sem comparacao.
- `FunctionPointService.process_fp_count_commit`: validar commit com e sem parent.
- `ContadorSFPApp.process_selection`: validar erros de selecao e roteamento de
  fluxo com mocks.

### 10.3 Testes de integracao com mocks

- Fluxo completo por branch com dois arquivos elegiveis.
- Fluxo completo por MR com diff misto.
- Fluxo por commit com diff elegivel e arquivo inacessivel.
- Falha parcial GitLab durante leitura de arquivo.
- Falha transitoria Azure OpenAI seguida de sucesso.

### 10.4 Testes de aceitacao

Cenario A: estimar tamanho funcional por branch.

- Dado um projeto GitLab valido.
- E um branch valido com arquivos elegiveis.
- Quando o usuario processa a selecao.
- Entao o sistema exibe o total de SFP e os elementos funcionais.

Cenario B: impedir escopo ambiguo.

- Dado um projeto GitLab valido.
- E branch e MR selecionados simultaneamente.
- Quando o usuario tenta processar.
- Entao o sistema exibe erro de exclusao mutua.

Cenario C: tolerar arquivo nao elegivel.

- Dado um escopo com arquivos suportados e nao suportados.
- Quando o processamento ocorre.
- Entao somente arquivos suportados contribuem para o total.

## 11. Dependencias e execucao

Dependencias externas Python:

- `openai`
- `python-dotenv`
- `python-gitlab`

Instalacao:

```powershell
pip install -r requirements.txt
```

Execucao:

```powershell
python ContadorSFP.py
```

Com ambiente virtual local:

```powershell
.\.venv\Scripts\Activate.ps1
python .\ContadorSFP.py
```

Execucao da suite de testes:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado esperado:

```text
22 passed
```

Observacao: a suite de testes e representativa, nao exaustiva. Ela demonstra a
aplicacao das tecnicas do artigo em cenarios selecionados do SUT. Os testes de
MBT foram derivados manualmente dos modelos documentados, com rastreabilidade
explicita para os arquivos de teste, e nao gerados automaticamente por uma
ferramenta de geracao de testes.

## 12. Configuracao do `.env`

Exemplo:

```text
AZURE_OPENAI_API_KEY=sua_chave_do_azure_openai
AZURE_OPENAI_ENDPOINT=https://seu-recurso.openai.azure.com/

GITLAB_ENDPOINT=https://gitlab.com
GITLAB_PRIVATE_TOKEN=seu_token_privado_do_gitlab

AZURE_OPENAI_TAMANHO_BLOCO=12000
AZURE_OPENAI_MAX_RETRIES=5
AZURE_OPENAI_RETRY_DELAY=10
```

Variaveis obrigatorias:

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `GITLAB_ENDPOINT`
- `GITLAB_PRIVATE_TOKEN`

Variaveis opcionais:

- `AZURE_OPENAI_TAMANHO_BLOCO`
- `AZURE_OPENAI_MAX_RETRIES`
- `AZURE_OPENAI_RETRY_DELAY`

## 13. Artefatos complementares da estrategia de qualidade

Este arquivo pode ser lido de forma independente como especificacao consolidada
do projeto. Os arquivos em `docs/` detalham os artefatos formais usados para
ligar a teoria do artigo ao codigo e aos testes.

- `docs/dominio_entrada.md`: detalha as caracteristicas de entrada, blocos,
  valores limite e cobertura representativa por MDE, CCE e CEB.
- `docs/contratos.md`: documenta pre-condicoes, pos-condicoes e invariantes dos
  componentes centrais do SUT.
- `docs/tabela_decisao_escopo.md`: explicita as regras de decisao para branch,
  MR, commit e entradas invalidas.
- `docs/maquina_estados_processamento.md`: descreve os estados e transicoes do
  processamento da contagem funcional.
- `docs/criterios_aceitacao_gore.md`: relaciona metas de negocio a cenarios de
  aceitacao.
- `docs/matriz_rastreabilidade.md`: conecta tecnica, elemento do artigo,
  implementacao e funcao de teste especifica.

Leitura recomendada:

1. Ler esta especificacao para entender o SUT e a estrategia geral.
2. Consultar `docs/matriz_rastreabilidade.md` para localizar a evidencia de
   teste de cada tecnica.
3. Abrir os arquivos em `tests/` para verificar como cada evidencia foi
   implementada.

## 14. Artefatos do projeto

- `prompt.txt`: template enviado ao Azure OpenAI.
- `resultado_intermediario.txt`: registro das respostas parciais aceitas.
- `execucao.log`: log de execucao.
- `requirements.txt`: dependencias externas.
- `readme.txt`: instrucoes de contexto, configuracao e execucao.
- `tests/`: suite automatizada representativa com pytest.
- `tests/test_contracts.py`: evidencia executavel de pre-condicoes,
  pos-condicoes e invariantes.
- `tests/fakes/`: simuladores de GitLab e Azure OpenAI usados pelos testes.
- `tests/conftest.py`: preparacao automatica do ambiente isolado de teste.
- `ARTIGO FINAL - DRAFT.txt`: texto local do artigo usado como contexto
  academico. Este arquivo nao e necessario para execucao do sistema.

## 15. Riscos e pontos de atencao

- O resultado depende da qualidade do prompt e da estabilidade do modelo de IA.
- A resposta da IA precisa ser JSON valido; respostas fora do contrato sao
  descartadas ou interrompem o bloco corrente.
- A interface usa strings formatadas para representar entidades selecionadas,
  como `"id: titulo"`. Esse formato deve ser preservado ou substituido por uma
  estrutura mais robusta em evolucoes futuras.
- O processamento faz chamadas de rede para GitLab e Azure OpenAI; testes
  automatizados devem usar mocks para evitar instabilidade.
- `DEPLOYMENT_NAME` esta fixo como `"StudioAI"` em `config.py`; se o deployment
  do Azure tiver outro nome, o codigo deve ser ajustado ou a configuracao deve
  ser externalizada em variavel de ambiente.

## 16. Criterios de aceite da especificacao

Esta especificacao e considerada atendida quando:

- O projeto pode ser instalado a partir de `requirements.txt`.
- A aplicacao inicia por `python ContadorSFP.py`.
- O `.env` contem as variaveis obrigatorias.
- O usuario consegue escolher projeto e escopo valido.
- O sistema processa branch, MR ou commit conforme regras definidas.
- O total de SFP exibido corresponde a soma das respostas validas da IA.
- Nenhuma credencial sensivel esta hardcoded no repositorio.
