import os
from dotenv import load_dotenv
import openai
import gitlab
import tkinter as tk
from tkinter import ttk
import logging
import json
import time

# Ajustar o nome do deployment para 'StudioAI' se este for o nome correto
deployment_name = 'StudioAI'

# Lista de extensões suportadas
extensoes_suportadas = ['.py', '.jsp', '.jspx', '.js', '.ts', '.groovy', '.kt', '.scala']

# Dicionários globais para mapear IDs
commit_map = {}
branch_map = {}
merge_request_map = {}

print("Iniciando script...")

# Configurar logging
logging.basicConfig(
    filename='execucao.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

print("Variáveis de ambiente carregadas...")

# Configurar Azure OpenAI
api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = "azure"
openai.api_version = "2024-02-01"  # Certifique-se de que esta seja a versão correta
openai.api_key = api_key
openai.azure_endpoint = azure_endpoint

print("Azure OpenAI configurado...")

# Configurar GitLab
gl = gitlab.Gitlab(os.getenv('GITLAB_ENDPOINT'), private_token=os.getenv('GITLAB_PRIVATE_TOKEN'))
print("GitLab configurado...")

# Função para obter projetos
def get_projects():
    print("Obtendo projetos...")
    return gl.projects.list(owned=True, all=True)

# Função para obter issues
def get_issues(project):
    issues = project.issues.list(all=True)
    issue_list = ["N/A"] + [f"{issue.iid}: {issue.title}" for issue in issues]
    return issue_list

# Função para obter branches
def get_branches(project, jira_key=None):
    branches = project.branches.list(all=True)
    branch_list = ["N/A"]
    for branch in branches:
        if jira_key:
            if jira_key.lower() in branch.name.lower():
                branch_list.append(f"{branch.name}")
        else:
            branch_list.append(f"{branch.name}")
    return branch_list

# Função para obter merge requests
def get_merge_requests(project, jira_key=None):
    merge_requests = project.mergerequests.list(all=True)
    mr_list = ["N/A"]
    for mr in merge_requests:
        if jira_key:
            if jira_key.lower() in mr.title.lower():
                mr_list.append(f"{mr.iid}: {mr.title}")
        else:
            mr_list.append(f"{mr.iid}: {mr.title}")
    return mr_list

# Função para obter commits
def get_commits(project, branch_name=None, mr_iid=None, jira_key=None):
    if branch_name and branch_name != "N/A":
        commits = project.commits.list(ref_name=branch_name, all=True)
    elif mr_iid and mr_iid != "N/A":
        mr = project.mergerequests.get(mr_iid)
        commits = mr.commits()
    else:
        commits = project.commits.list(all=True)

    commit_list = ["N/A"]
    for commit in commits:
        if jira_key:
            if jira_key.lower() in commit.title.lower():
                commit_map[commit.short_id] = commit.id
                commit_list.append(f"{commit.short_id}: {commit.title}")
        else:
            commit_map[commit.short_id] = commit.id
            commit_list.append(f"{commit.short_id}: {commit.title}")
    return commit_list

# Função para atualizar issues e branches ao selecionar um projeto
def update_issues(*args):
    project_id = int(project_var.get().split(":")[0])
    project = gl.projects.get(project_id)
    
    # Atualizar a lista de issues
    issues = get_issues(project)
    issue_combobox['values'] = issues
    issue_var.set("N/A")
    
    # Atualizar a lista de branches sem precisar de uma issue
    branches = get_branches(project)
    branch_combobox['values'] = branches
    branch_var.set("N/A")
    
    # Limpar os próximos comboboxes
    mr_combobox['values'] = ["N/A"]
    merge_request_var.set("N/A")
    commit_combobox['values'] = ["N/A"]
    commit_var.set("N/A")

# Função para atualizar branches, merge requests e commits ao selecionar uma issue
def update_branches_mrs(*args):
    project_id = int(project_var.get().split(":")[0])
    project = gl.projects.get(project_id)
    
    selected_issue = issue_var.get()
    jira_key = None

    # Se uma issue for selecionada e não for "N/A", extraímos o código JIRA
    if selected_issue != "N/A":
        issue_description = selected_issue.split(":")[1].strip()
        jira_key = issue_description.split()[0]  # Extrair o código JIRA da descrição da issue

    # Atualiza a lista de branches: se jira_key for None, retorna todos os branches; caso contrário, filtra
    branches = get_branches(project, jira_key)
    branch_combobox['values'] = branches
    branch_var.set("N/A")
    
    # Atualiza a lista de merge requests da issue selecionada
    mrs = get_merge_requests(project, jira_key)
    mr_combobox['values'] = mrs
    merge_request_var.set("N/A")
    
    # Atualiza a lista de commits relacionados à issue (se houver branch ou merge request relacionado)
    commits = get_commits(project, jira_key=jira_key)  # Filtra os commits pela issue
    commit_combobox['values'] = commits
    commit_var.set("N/A")

# Função para atualizar commits ao selecionar um branch
def update_commits_branch(*args):
    # Verifica se o valor selecionado em 'Selecione um Branch' não é "N/A"
    if branch_var.get() != "N/A":
        # Se um branch foi selecionado, o merge request é automaticamente redefinido para "N/A"
        merge_request_var.set("N/A")
        
        # Limpar os commits, pois estamos selecionando um branch, não um merge request
        commit_var.set("N/A")
        commit_combobox['values'] = ["N/A"]
        
        # Adicionar uma mensagem informando ao usuário que o merge request foi redefinido
        output_label.config(text="Selecionando um branch, o merge request foi redefinido para 'N/A'.")
        
        # Obter o ID do projeto selecionado
        project_id = int(project_var.get().split(":")[0])
        project = gl.projects.get(project_id)
        
        # Verificar se uma issue foi selecionada e obter o código JIRA associado
        selected_issue = issue_var.get()
        jira_key = None
        if selected_issue != "N/A":
            issue_description = selected_issue.split(":")[1].strip()
            jira_key = issue_description.split()[0]
        
        # Obter a lista de commits do branch selecionado (possivelmente filtrando por uma issue)
        commits = get_commits(project, branch_name=branch_var.get(), jira_key=jira_key)
        
        # Atualizar a combobox de commits com os commits obtidos
        commit_combobox['values'] = commits
        
        # Garantir que a seleção do commit seja redefinida
        commit_var.set("N/A")

# Função para atualizar commits ao selecionar um merge request
def update_commits_mr(*args):
    if merge_request_var.get() != "N/A":
        # Ao selecionar um merge request, limpe a seleção de branch e commits
        branch_var.set("N/A")
        commit_var.set("N/A")
        commit_combobox['values'] = ["N/A"]

        project_id = int(project_var.get().split(":")[0])
        project = gl.projects.get(project_id)
        mr_iid = merge_request_var.get().split(":")[0]
        commits = get_commits(project, mr_iid=mr_iid)
        commit_combobox['values'] = ["N/A"]  # Desabilita a seleção de commits, pois não é aplicável ao merge request

# Função para processar a seleção
def process_selection():
    # Captura o timestamp do início do processamento
    timestamp_inicio = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    # Captura os valores selecionados pelo usuário
    selected_project = project_var.get()
    selected_issue = issue_var.get()
    selected_branch = branch_var.get()
    selected_mr = merge_request_var.get()
    selected_commit_text = commit_var.get()

    # Verifica se o projeto foi selecionado
    if not selected_project:
        output_label.config(text="Erro: Selecione um projeto.")
        return

    project_id = int(selected_project.split(":")[0])
    project = gl.projects.get(project_id)

    # Validação: garantir que apenas um branch ou merge request esteja selecionado
    if selected_branch != "N/A" and selected_mr != "N/A":
        output_label.config(text="Erro: Não é possível selecionar ambos, branch e merge request.")
        return

    # Adicionar as informações ao JSON final (timestamp e valores da interface)
    metadata_info = {
        "Timestamp_Inicio": timestamp_inicio,
        "Projeto": selected_project,
        "Issue": selected_issue if selected_issue != "N/A" else "N/A",
        "Branch": selected_branch if selected_branch != "N/A" else "N/A",
        "Merge_Request": selected_mr if selected_mr != "N/A" else "N/A",
        "Commit": selected_commit_text if selected_commit_text != "N/A" else "N/A"
    }

    if selected_mr != "N/A":
        # Processar usando o merge request selecionado (comparação entre source e target branch)
        mr_iid = selected_mr.split(":")[0]
        mr = project.mergerequests.get(mr_iid)
        source_branch = mr.source_branch
        target_branch = mr.target_branch
        estimativa_fp = process_fp_count(project, source_branch, target_branch, compare=True, metadata_info=metadata_info)
        output_label.config(text=f"TOTAL GERAL DE SFP: {estimativa_fp}")
    
    elif selected_branch != "N/A":
        # Processar usando o branch selecionado sem comparação com outro branch (todos os arquivos do branch)
        source_branch = selected_branch
        
        if selected_commit_text == "N/A":
            # Se o commit estiver como "N/A", contar todos os arquivos no branch
            estimativa_fp = process_fp_count(project, source_branch, None, compare=False, metadata_info=metadata_info)
            output_label.config(text=f"TOTAL GERAL DE SFP: {estimativa_fp}")
        else:
            # Se um commit foi selecionado, processar o commit específico
            selected_commit_id = commit_map.get(selected_commit_text.split(":")[0])
            if not selected_commit_id:
                output_label.config(text="Erro: Commit selecionado não encontrado.")
                return
            estimativa_fp = process_fp_count_commit(project, selected_commit_id, metadata_info=metadata_info)
            output_label.config(text=f"TOTAL GERAL DE SFP: {estimativa_fp}")

    else:
        output_label.config(text="Erro: Selecione um merge request, branch ou commit.")

# Função para processar a contagem de FP comparando branches
def process_fp_count(project, source_branch, target_branch=None, compare=True, metadata_info=None):
    if not compare:
        print(f"Processando todos os arquivos no branch {source_branch}...")
        files = project.repository_tree(ref=source_branch, recursive=True)
        resultado_total = {"Total_SFP": 0, "Elementos_FP": []}
        
        # Processar os arquivos
        with open('resultado_intermediario.txt', 'w') as resultado_intermediario:
            for file in files:
                path = file['path']
                if not any(path.endswith(ext) for ext in extensoes_suportadas):
                    logging.info(f"Ignorando arquivo {path} - Extensão não suportada")
                    continue

                logging.info(f"Processando arquivo {path} no branch {source_branch}")

                # Obter o conteúdo do arquivo no branch
                try:
                    file_content = project.files.get(file_path=path, ref=source_branch).decode().decode('utf-8')
                except gitlab.exceptions.GitlabGetError as e:
                    logging.error(f"Erro ao obter o arquivo {path} no branch {source_branch}: {e}")
                    continue

                conteudo_arquivos = {path: file_content}
                descricao_detalhada = gerar_descricao_detalhada(conteudo_arquivos)
                descricao_projeto = gerar_descricao_projeto([{'path': path, 'type': 'blob'}])

                try:
                    resposta = consultar_especialista_ai(f"Arquivo {path} no branch {source_branch}", descricao_detalhada, path)
                    if resposta:
                        resultado_total['Total_SFP'] += resposta.get('Total_SFP', 0)
                        resultado_total["Elementos_FP"].extend(resposta.get("Elementos_FP", []))
                        # Escrever no arquivo intermediário
                        resultado_intermediario.write(json.dumps(resposta) + "\n")
                except Exception as e:
                    logging.error(f"Erro ao processar o arquivo {path}: {e}")

        # Incluir as informações da interface e timestamp no JSON de retorno
        resultado_total['Metadata'] = metadata_info

        preencher_grid(resultado_total["Elementos_FP"])
        return resultado_total['Total_SFP']

    else:
        # Comparar dois branches
        print(f"Comparando {source_branch} com {target_branch}...")
        try:
            comparison = project.repository_compare(from_=target_branch, to=source_branch)
            diffs = comparison['diffs']
        except Exception as e:
            print(f"Erro ao comparar os branches: {e}")
            logging.error(f"Erro ao comparar os branches: {e}")
            output_label.config(text="Erro ao comparar os branches.")
            return 0

        resultado_total = {"Total_SFP": 0, "Elementos_FP": []}

        with open('resultado_intermediario.txt', 'w') as resultado_intermediario:
            for diff in diffs:
                path = diff.get('new_path') or diff.get('old_path')
                if not path or not any(path.endswith(ext) for ext in extensoes_suportadas):
                    logging.info(f"Ignorando arquivo {path} - Extensão não suportada")
                    continue

                logging.info(f"Processando arquivo {path} no branch {source_branch}")

                # Obter o conteúdo do arquivo no branch source
                try:
                    file_content = project.files.get(file_path=path, ref=source_branch).decode().decode('utf-8')
                except gitlab.exceptions.GitlabGetError as e:
                    logging.error(f"Erro ao obter o arquivo {path} no branch {source_branch}: {e}")
                    continue

                conteudo_arquivos = {path: file_content}
                descricao_detalhada = gerar_descricao_detalhada(conteudo_arquivos)
                descricao_projeto = gerar_descricao_projeto([{'path': path, 'type': 'blob'}])

                try:
                    resposta = consultar_especialista_ai(f"Alterações no arquivo {path}", descricao_detalhada, path)
                    if resposta:
                        resultado_total['Total_SFP'] += resposta.get('Total_SFP', 0)
                        resultado_total["Elementos_FP"].extend(resposta.get("Elementos_FP", []))
                        # Escrever no arquivo intermediário
                        resultado_intermediario.write(json.dumps(resposta) + "\n")
                except Exception as e:
                    logging.error(f"Erro ao processar o arquivo {path}: {e}")

        preencher_grid(resultado_total["Elementos_FP"])
        return resultado_total['Total_SFP']
    
# Função para processar commits
def process_fp_count_commit(project, selected_commit_id, metadata_info=None):
    print("Processando contagem de Function Points para o commit selecionado...")

    # Obter o commit anterior
    previous_commit = get_previous_commit(project, selected_commit_id)
    if previous_commit:
        diffs = get_diff_between_commits(project, previous_commit.id, selected_commit_id)
    else:
        commit = project.commits.get(selected_commit_id)
        diffs = commit.diff()

    resultado_total = {"Total_SFP": 0, "Elementos_FP": []}

    # Processar as diferenças entre os commits
    with open('resultado_intermediario.txt', 'w') as resultado_intermediario:
        for diff in diffs:
            path = diff.get('new_path') or diff.get('old_path')
            if not path or not any(path.endswith(ext) for ext in extensoes_suportadas):
                continue

            try:
                file_content = project.files.get(file_path=path, ref=selected_commit_id).decode().decode('utf-8')
            except gitlab.exceptions.GitlabGetError as e:
                print(f"Erro ao obter o arquivo {path} no commit {selected_commit_id}: {e}")
                continue

            conteudo_arquivos = {path: file_content}
            descricao_detalhada = gerar_descricao_detalhada(conteudo_arquivos)
            descricao_projeto = gerar_descricao_projeto([{'path': path, 'type': 'blob'}])

            try:
                resposta = consultar_especialista_ai(f"Alterações no arquivo {path}", descricao_detalhada, path)
                if resposta:
                    resultado_total['Total_SFP'] += resposta.get('Total_SFP', 0)
                    resultado_total["Elementos_FP"].extend(resposta.get("Elementos_FP", []))
                    # Escrever no arquivo intermediário
                    resultado_intermediario.write(json.dumps(resposta) + "\n")
            except Exception as e:
                print(f"Erro ao processar o arquivo {path}: {e}")

    # Incluir as informações da interface e timestamp no JSON de retorno
    resultado_total['Metadata'] = metadata_info

    preencher_grid(resultado_total["Elementos_FP"])
    return resultado_total['Total_SFP']

    # Processar as diferenças
    with open('resultado_intermediario.txt', 'w') as resultado_intermediario:
        for diff in diffs:
            path = diff.get('new_path') or diff.get('old_path')
            if not path or not any(path.endswith(ext) for ext in extensoes_suportadas):
                continue

            # Obter o conteúdo do arquivo no commit selecionado
            try:
                file_content = project.files.get(file_path=path, ref=selected_commit_id).decode().decode('utf-8')
            except gitlab.exceptions.GitlabGetError as e:
                print(f"Erro ao obter o arquivo {path} no commit {selected_commit_id}: {e}")
                continue

            conteudo_arquivos = {path: file_content}
            descricao_detalhada = gerar_descricao_detalhada(conteudo_arquivos)
            descricao_projeto = gerar_descricao_projeto([{'path': path, 'type': 'blob'}])

            try:
                resposta = consultar_especialista_ai(f"Alterações no arquivo {path}", descricao_detalhada, path)
                if resposta:
                    resultado_total['Total_SFP'] += resposta.get('Total_SFP', 0)
                    resultado_total["Elementos_FP"].extend(resposta.get("Elementos_FP", []))
                    resultado_intermediario.write(json.dumps(resposta) + "\n")
            except Exception as e:
                print(f"Erro ao processar o arquivo {path}: {e}")

    preencher_grid(resultado_total["Elementos_FP"])
    return resultado_total['Total_SFP']

# Função para obter o commit anterior
def get_previous_commit(project, commit_id):
    commits = project.commits.list(ref_name='master', all=True)
    for i, commit in enumerate(commits):
        if commit.id.strip() == commit_id.strip():
            return commits[i + 1] if i + 1 < len(commits) else None
    return None

# Função para obter as diferenças entre dois commits
def get_diff_between_commits(project, from_commit_id, to_commit_id):
    comparison = project.repository_compare(from_commit_id, to_commit_id)
    return comparison['diffs']

# Função para ler o conteúdo dos arquivos
def ler_arquivos_codigo(files, project):
    conteudo = {}
    for file in files:
        if file.get('type') == 'blob' and any(file['path'].endswith(ext) for ext in extensoes_suportadas):
            try:
                file_content = project.files.get(file_path=file['path'], ref='master').decode().decode('utf-8')
                conteudo[file['path']] = file_content
            except gitlab.GitlabGetError as e:
                print(f"Erro ao ler o arquivo {file['path']}: {e}")
            except Exception as e:
                print(f"Erro inesperado ao ler o arquivo {file['path']}: {e}")
    return conteudo

# Função para gerar a descrição do projeto
def gerar_descricao_projeto(files):
    descricao = "Descrição do Projeto: O sistema contém os seguintes componentes:\n"
    componentes = []

    for file in files:
        if file.get('type') == 'blob' and any(file['path'].endswith(ext) for ext in extensoes_suportadas):
            componentes.append(f"Arquivo: {file['path']} - Tipo: {file.get('type', 'desconhecido')}")

    if componentes:
        descricao += "\n".join(componentes)
    else:
        descricao += "Nenhum componente relevante encontrado.\n"

    descricao += "\n"
    return descricao

# Função para gerar a descrição detalhada
def gerar_descricao_detalhada(conteudo_arquivos):
    descricao_detalhada = "Descrição detalhada dos arquivos:\n"
    for path, content in conteudo_arquivos.items():
        descricao_detalhada += f"Arquivo: {path}\nConteúdo:\n{content}\n"
    return descricao_detalhada

# Função para consultar a API da Azure OpenAI
def consultar_especialista_ai(descricao_projeto, descricao_detalhada, caminho_arquivo):
    TAMANHO_BLOCO = int(os.getenv('AZURE_OPENAI_TAMANHO_BLOCO', 12000))
    MAX_RETRIES = int(os.getenv('AZURE_OPENAI_MAX_RETRIES', 5))
    RETRY_DELAY = int(os.getenv('AZURE_OPENAI_RETRY_DELAY', 10))

    blocos = [descricao_detalhada[i:i + TAMANHO_BLOCO] for i in range(0, len(descricao_detalhada), TAMANHO_BLOCO)]
    resultado_total = {"Total_SFP": 0, "Elementos_FP": []}

    for i, bloco in enumerate(blocos):
        print(f"Processando bloco {i+1}/{len(blocos)} do arquivo {caminho_arquivo}...")

        with open('prompt.txt', 'r', encoding='utf-8') as file:
            prompt_template = file.read()

        prompt = prompt_template.replace('{{descricao_projeto}}', descricao_projeto).replace('{{descricao_detalhada}}', bloco)

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"{descricao_projeto}\n\n{bloco}\nArquivo: {caminho_arquivo}"}
        ]

        for tentativa in range(MAX_RETRIES):
            try:
                response = openai.chat.completions.create(
                            model=deployment_name,  # substitui "model" por "engine" 
                            messages=messages,
                            max_tokens=3000,
                            temperature=0.2,
                            top_p=1.0,
                            frequency_penalty=0.0,
                            presence_penalty=0.0
                )

                content = response.choices[0].message.content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]

                resposta = json.loads(content)

                resultado_total['Total_SFP'] += resposta.get('Total_SFP', 0)
                resultado_total["Elementos_FP"].extend(resposta.get("Elementos_FP", []))

                break

            except openai.OpenAIError as e:
                print(f"Erro da API ao acessar o assistente AI para o bloco {i+1}: {e}")
                time.sleep(RETRY_DELAY)
            except json.JSONDecodeError:
                print("Erro ao decodificar a resposta da API.")
                break
            except Exception as e:
                print(f"Erro inesperado ao acessar o assistente AI para o bloco {i+1}: {e}")
                break

    return resultado_total

# Função para preencher a grid
def preencher_grid(elementos_fp):
    # Limpar grid atual
    for i in tree.get_children():
        tree.delete(i)

    # Preencher com novos elementos
    for item in elementos_fp:
        try:
            nome_arquivo_completo = item.get('Nome_Arquivo', 'Desconhecido')
            extensao = item.get('Extensao', '')
            if not extensao:
                nome_arquivo, extensao = os.path.splitext(nome_arquivo_completo)
                extensao = extensao.lstrip('.')
            else:
                nome_arquivo = os.path.splitext(nome_arquivo_completo)[0]
            extensao = extensao.lstrip('.')
            elemento_fp = item.get('Elemento_FP', 'Desconhecido')
            pontos = item.get('Pontos', 0)

            tree.insert('', 'end', values=(nome_arquivo, extensao, elemento_fp, pontos))
        except KeyError as e:
            print(f"Erro ao preencher a grid, chave ausente: {e}")
            logging.error(f"Erro ao preencher a grid, chave ausente: {e}")

# Configurar a janela principal
janela = tk.Tk()
janela.title("CONTADOR DE PONTOS DE FUNÇÃO")

# Criar variáveis tkinter
project_var = tk.StringVar()
issue_var = tk.StringVar()
branch_var = tk.StringVar()
merge_request_var = tk.StringVar()
commit_var = tk.StringVar()

# Obter projetos
projects = get_projects()

# Label e ComboBox para projetos
tk.Label(janela, text="Selecione um Projeto:").grid(row=0, column=0, padx=10, pady=10)
project_combobox = ttk.Combobox(janela, textvariable=project_var, values=[f"{project.id}: {project.name}" for project in projects], width=80)
project_combobox.grid(row=0, column=1, padx=10, pady=10)
project_combobox.bind("<<ComboboxSelected>>", update_issues)

# Label e ComboBox para issues
tk.Label(janela, text="Selecione uma Issue:").grid(row=1, column=0, padx=10, pady=10)
issue_combobox = ttk.Combobox(janela, textvariable=issue_var, width=80)
issue_combobox.grid(row=1, column=1, padx=10, pady=10)
issue_combobox.bind("<<ComboboxSelected>>", update_branches_mrs)

# Label e ComboBox para branches
tk.Label(janela, text="Selecione um Branch:").grid(row=2, column=0, padx=10, pady=10)
branch_combobox = ttk.Combobox(janela, textvariable=branch_var, width=80)
branch_combobox.grid(row=2, column=1, padx=10, pady=10)
branch_combobox.bind("<<ComboboxSelected>>", update_commits_branch)

# Label e ComboBox para merge requests
tk.Label(janela, text="Selecione um Merge Request:").grid(row=3, column=0, padx=10, pady=10)
mr_combobox = ttk.Combobox(janela, textvariable=merge_request_var, width=80)
mr_combobox.grid(row=3, column=1, padx=10, pady=10)
mr_combobox.bind("<<ComboboxSelected>>", update_commits_mr)

# Label e ComboBox para commits
tk.Label(janela, text="Selecione um Commit:").grid(row=4, column=0, padx=10, pady=10)
commit_combobox = ttk.Combobox(janela, textvariable=commit_var, width=80)
commit_combobox.grid(row=4, column=1, padx=10, pady=10)

# Configurar o grid para exibir os elementos FP com 4 colunas
tree = ttk.Treeview(janela, columns=("Nome_Arquivo", "Extensao", "Elemento_FP", "Pontos"), show='headings')

# Definir os cabeçalhos das 4 colunas
tree.heading("Nome_Arquivo", text="Nome do Arquivo")
tree.heading("Extensao", text="Extensão")
tree.heading("Elemento_FP", text="Elemento FP")
tree.heading("Pontos", text="Pontos")

# Ajustar a largura das colunas (opcional)
tree.column("Nome_Arquivo", width=200)
tree.column("Extensao", width=100)
tree.column("Elemento_FP", width=150)
tree.column("Pontos", width=50)

# Posicionar o grid na interface
tree.grid(row=5, columnspan=2, padx=10, pady=10)

# Botão de Processar
process_button = tk.Button(janela, text="Processar Seleção", command=process_selection)
process_button.grid(row=6, columnspan=2, pady=20)

# Área para mostrar a saída da estimativa de Function Points
output_label = tk.Label(janela, text="", fg="blue")
output_label.grid(row=7, columnspan=2, pady=10)

# Iniciar o loop da interface gráfica
janela.mainloop()