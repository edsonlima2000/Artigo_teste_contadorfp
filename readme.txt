Contador de Pontos de Funcao
============================

Este repositorio contem o Sistema Sob Teste (SUT) utilizado em um artigo
academico de Mestrado em Computacao Aplicada, na disciplina de Qualidade e
Teste de Software.

O SUT e um Contador Automatizado de Pontos de Funcao (SFP), desenvolvido em
Python, com interface grafica em Tkinter, integracao com a API do GitLab e uso
do Azure OpenAI para apoiar a classificacao funcional de alteracoes de codigo.
O sistema analisa artefatos de software a partir de branches, commits e merge
requests, estimando o impacto funcional das mudancas.

No contexto do artigo, o projeto serve como base pratica para demonstrar a
aplicacao integrada de tecnicas de Qualidade e Teste de Software, incluindo:

- Modelagem do Dominio da Entrada (MDE), com criterios CCE e CEB.
- Teste Baseado em Contratos, com pre-condicoes, pos-condicoes e invariantes.
- Teste Baseado em Modelos (MBT), usando tabelas de decisao e maquinas de
  estados.
- Teste de Aceitacao orientado a metas de negocio (GORE).

A analise academica delimita o foco no modulo de processamento da contagem
funcional, especialmente nos fluxos associados a recuperacao de artefatos do
GitLab, filtragem de arquivos elegiveis, chamada ao especialista de IA e
consolidacao do total de SFP.

Este projeto usa variaveis de ambiente para configurar o acesso ao GitLab e ao Azure OpenAI.
Crie um arquivo chamado .env na raiz do projeto, na mesma pasta do ContadorSFP.py.

Exemplo de .env
---------------

AZURE_OPENAI_API_KEY=sua_chave_do_azure_openai
AZURE_OPENAI_ENDPOINT=https://seu-recurso.openai.azure.com/

GITLAB_ENDPOINT=https://gitlab.com
GITLAB_PRIVATE_TOKEN=seu_token_privado_do_gitlab

AZURE_OPENAI_TAMANHO_BLOCO=12000
AZURE_OPENAI_MAX_RETRIES=5
AZURE_OPENAI_RETRY_DELAY=10

Variaveis obrigatorias
----------------------

AZURE_OPENAI_API_KEY
Chave de API do recurso Azure OpenAI.

AZURE_OPENAI_ENDPOINT
Endpoint do recurso Azure OpenAI. Normalmente fica no formato:
https://nome-do-recurso.openai.azure.com/

GITLAB_ENDPOINT
URL base da instancia GitLab. Para GitLab publico, use:
https://gitlab.com

GITLAB_PRIVATE_TOKEN
Token pessoal do GitLab com permissao para ler projetos, issues, branches,
merge requests, commits e arquivos do repositorio que sera analisado.

Variaveis opcionais
-------------------

AZURE_OPENAI_TAMANHO_BLOCO
Tamanho maximo de cada bloco de texto enviado ao modelo. Valor padrao: 12000.

AZURE_OPENAI_MAX_RETRIES
Quantidade maxima de tentativas em caso de erro na chamada ao Azure OpenAI.
Valor padrao: 5.

AZURE_OPENAI_RETRY_DELAY
Tempo de espera, em segundos, entre tentativas de chamada ao Azure OpenAI.
Valor padrao: 10.

Como executar
-------------

1. Crie e preencha o arquivo .env na raiz do projeto.
2. Instale as dependencias:

   pip install -r requirements.txt

3. Execute a aplicacao:

   python ContadorSFP.py

Como executar os testes
-----------------------

O projeto inclui uma suite pytest com fakes de GitLab e Azure OpenAI para validar
os cenarios do artigo sem depender de chamadas de rede.

A suite de testes nao tem objetivo de ser exaustiva. Ela foi construida como
evidencia representativa das tecnicas discutidas no artigo academico:

- Modelagem do Dominio da Entrada (MDE).
- Cobertura de Cada Escolha (CCE).
- Escolha da Base (CEB).
- Teste Baseado em Contratos.
- Teste Baseado em Modelos (MBT).
- Teste de Aceitacao orientado por metas (GORE).
- Rastreabilidade entre tecnica, requisito, codigo e teste.

Assim, os testes demonstram a aplicacao pratica das tecnicas em cenarios
selecionados do SUT, sem pretender cobrir todas as combinacoes possiveis de uso,
falha ou integracao.

Organizacao dos testes
----------------------

- `tests/`: contem os testes automatizados do projeto.
- `tests/fakes/`: contem objetos falsos que simulam GitLab e Azure OpenAI.
- `tests/conftest.py`: prepara automaticamente o ambiente de cada teste.

Os fakes permitem controlar entradas e saidas sem acessar servicos externos.
Assim, os testes nao precisam de internet, token GitLab, chave Azure OpenAI ou
consumo real de API. Isso torna a execucao mais rapida, repetivel e adequada ao
contexto academico do artigo.

O `conftest.py` cria uma pasta temporaria para cada teste, gera um `prompt.txt`
temporario e configura variaveis de ambiente de teste. Isso evita que a suite
altere arquivos reais do projeto durante a execucao.

Se o ambiente virtual estiver ativado, execute:

   pytest

Ou execute diretamente pelo Python do ambiente virtual:

   .\.venv\Scripts\python.exe -m pytest -q

Resultado esperado:

   17 passed

Observacoes de seguranca
------------------------

- Nunca publique o arquivo .env.
- O .gitignore deste projeto ja ignora .env.
- Se algum token for exposto, revogue o token no GitLab ou Azure e gere outro.
