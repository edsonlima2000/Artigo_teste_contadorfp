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

# Dicionário global para mapear o ID curto para o ID completo
commit_map = {}

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
#openai.api_version = "AZURE_OPENAI_VERSION"  # Certifique-se de que esta seja a versão correta
openai.api_version = "2024-02-01"  # Substitua pela versão correta da API
openai.api_key = api_key
openai.azure_endpoint = azure_endpoint

print("Azure OpenAI configurado...")

# Configurar GitLab
gl = gitlab.Gitlab(os.getenv('GITLAB_ENDPOIT'), private_token=os.getenv('GITLAB_PRIVATE_TOKEN'))
print("GitLab configurado...")

# Função para obter projetos
def get_projects():
    print("Obtendo projetos...")
    return gl.projects.list(owned=True, all=True)

# Função para obter issues
def get_issues(project):
    return project.issues.list(all=True)

# Função para obter commits
def get_commits(project):
    return project.commits.list(ref_name='master', all=True)

# Função para obter o commit anterior
def get_previous_commit(project, commit_id):
    commits = project.commits.list(ref_name='master', all=True)
    for i, commit in enumerate(commits):
        if commit.id.strip() == commit_id.strip():
            return commits[i + 1] if i + 1 < len(commits) else None
    return None

# Função para obter as diferenças entre dois commits
def get_diff_between_commits(project, current_commit_id, previous_commit_id):
    comparison = project.repository_compare(previous_commit_id, current_commit_id)
    return comparison['diffs']

# Função para obter commits filtrados pela chave do Jira
def get_filtered_commits(selected_project):
    project_id = int(selected_project.split(":")[0])
    project = gl.projects.get(project_id)
    commits = get_commits(project)

    issue_description = issue_var.get().split(":")[1].strip()
    jira_key = issue_description.split()[0]

    return [commit for commit in commits if jira_key.lower() in commit.title.lower()]

# Função para atualizar commits ao selecionar um issue
def update_commit_combobox(*args):
    commits = get_filtered_commits(project_var.get())
    if commits:
        commit_map.clear()
        combobox_values = []
        for commit in commits:
            short_id = commit.short_id
            commit_map[short_id] = commit.id
            combobox_values.append(f"{short_id}: {commit.title}")
        commit_combobox['values'] = ["Branch"] + combobox_values

# Função para atualizar issues e limpar commits ao selecionar um projeto
def update_issues_commits(*args):
    project_id = int(project_var.get().split(":")[0])
    project = gl.projects.get(project_id)
    issues = get_issues(project)
    issue_combobox['values'] = [f"{issue.iid}: {issue.title}" for issue in issues]
    commit_combobox['values'] = []

# Função para processar a seleção
def process_selection():
    selected_project = project_var.get()
    selected_issue = issue_var.get()
    selected_commit_text = commit_var.get()

    selected_commit_id = "Branch" if selected_commit_text == "Branch" else commit_map.get(selected_commit_text.split(":")[0])
    if not selected_project or not selected_issue or not selected_commit_id:
        output_label.config(text="Erro: Selecione um projeto, uma issue e um commit ou Branch.")
        return

    estimativa_fp = process_fp_count(selected_project, selected_commit_id)
    output_label.config(text=f"TOTAL GERAL DE SFP: {estimativa_fp}")

# Função para processar contagem de FP
def process_fp_count(selected_project, selected_commit_id):
    print("Processando contagem de Function Points...")
    project_id = int(selected_project.split(":")[0])
    project = gl.projects.get(project_id)

    if selected_commit_id == "Branch":
        files = project.repository_tree(ref='master', recursive=True)
        diffs = files
        use_new_path = False
    else:
        previous_commit = get_previous_commit(project, selected_commit_id)
        diffs = get_diff_between_commits(project, selected_commit_id, previous_commit.id) if previous_commit else project.repository_tree(ref='master', recursive=True)
        use_new_path = bool(previous_commit)

    resultado_total = {"Total_SFP": 0, "Elementos_FP": []}

    # Processar arquivo por arquivo
    with open('resultado_intermediario.txt', 'w') as resultado_intermediario:
        for diff in diffs:
            path = diff.get('new_path' if use_new_path else 'path')
            if not path or not any(path.endswith(ext) for ext in extensoes_suportadas):
                continue

            # Ler o conteúdo do arquivo individualmente
            conteudo_arquivo = ler_arquivos_codigo([{'path': path, 'type': 'blob'}], project)
            descricao_detalhada = gerar_descricao_detalhada(conteudo_arquivo)
            descricao_projeto = gerar_descricao_projeto([{'path': path, 'type': 'blob'}])

            try:
                # Processar o arquivo imediatamente
                resposta = consultar_especialista_ai(f"Alterações no arquivo {path}: {diff.get('diff', '')}", descricao_detalhada, path)
                if resposta:
                    resultado_total['Total_SFP'] += resposta.get('Total_SFP', 0)
                    resultado_total["Elementos_FP"].extend(resposta.get("Elementos_FP", []))
                    resultado_intermediario.write(json.dumps(resposta) + "\n")
            except Exception as e:
                print(f"Erro ao processar o arquivo {path}: {e}")

    preencher_grid(resultado_total["Elementos_FP"])
    return resultado_total['Total_SFP']

# Função para ler o arquivo e preencher a grid
def ler_arquivo_e_preencher_grid():
    try:
        with open('resultado_intermediario.txt', 'r') as file:
            elementos_fp = []
            for linha in file:
                resposta = json.loads(linha)
                elementos_fp.extend(resposta.get("Elementos_FP", []))
            preencher_grid(elementos_fp)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erro ao ler arquivo: {e}")

# Função para preencher a grid
def preencher_grid(elementos_fp):
    # Limpar grid atual
    for i in tree.get_children():
        tree.delete(i)

    # Preencher com novos elementos
    for item in elementos_fp:
        try:
            # Obter o nome do arquivo e a extensão separadamente
            nome_arquivo_completo = item.get('Nome_Arquivo', 'Desconhecido')
            
            # Verificar se a extensão já está presente
            extensao = item.get('Extensao', '')  
            
            if not extensao:
                # Se a extensão não for fornecida diretamente, extrair do nome do arquivo
                nome_arquivo, extensao = os.path.splitext(nome_arquivo_completo)
                # Remover o ponto da extensão
                extensao = extensao.lstrip('.')
            else:
                nome_arquivo = os.path.splitext(nome_arquivo_completo)[0]  # Pegar apenas o nome

            # Tratar casos onde a extensão esteja com o ponto no JSON
            extensao = extensao.lstrip('.')

            # Definir valores padrão para Elemento_FP e Pontos
            elemento_fp = item.get('Elemento_FP', 'Desconhecido')
            pontos = item.get('Pontos', 0)

            # Inserir os dados no grid
            tree.insert('', 'end', values=(nome_arquivo, extensao, elemento_fp, pontos))
        except KeyError as e:
            print(f"Erro ao preencher a grid, chave ausente: {e}")
            logging.error(f"Erro ao preencher a grid, chave ausente: {e}")

# Função para ler o conteúdo dos arquivos
def ler_arquivos_codigo(files, project):
    conteudo = {}
    for file in files:
        # Verificar se a chave 'type' está presente
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
        # Verificar se a chave 'type' está presente
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

# Função para consultar a API da Azure OpenAI, com blocos de até 12.000 caracteres
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
                # Enviar a requisição para o modelo Azure OpenAI
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

            # Substituindo 'openai.error' por 'openai.OpenAIError' que captura erros da API
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

# Configurar a janela principal
janela = tk.Tk()
janela.title("CONTADOR DE PONTOS DE FUNÇÃO")

# Criar variáveis tkinter
project_var = tk.StringVar()
issue_var = tk.StringVar()
commit_var = tk.StringVar()

# Obter projetos
projects = get_projects()

# Label e ComboBox para projetos
tk.Label(janela, text="Selecione um Projeto:").grid(row=0, column=0, padx=10, pady=10)
project_combobox = ttk.Combobox(janela, textvariable=project_var, values=[f"{project.id}: {project.name}" for project in projects], width=80)
project_combobox.grid(row=0, column=1, padx=10, pady=10)
project_combobox.bind("<<ComboboxSelected>>", update_issues_commits)

# Label e ComboBox para issues
issue_combobox = ttk.Combobox(janela, textvariable=issue_var, width=80)
tk.Label(janela, text="Selecione uma Issue:").grid(row=1, column=0, padx=10, pady=10)
issue_combobox.grid(row=1, column=1, padx=10, pady=10)
issue_combobox.bind("<<ComboboxSelected>>", update_commit_combobox)

# Label e ComboBox para commits
commit_combobox = ttk.Combobox(janela, textvariable=commit_var, width=80)
tk.Label(janela, text="Selecione um Commit:").grid(row=2, column=0, padx=10, pady=10)
commit_combobox.grid(row=2, column=1, padx=10, pady=10)

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
tree.grid(row=3, columnspan=2, padx=10, pady=10)

# Botão de Processar
process_button = tk.Button(janela, text="Processar Seleção", command=process_selection)
process_button.grid(row=4, columnspan=2, pady=20)

# Área para mostrar a saída da estimativa de Function Points
output_label = tk.Label(janela, text="", fg="blue")
output_label.grid(row=5, columnspan=2, pady=10)

# Iniciar o loop da interface gráfica
janela.mainloop()