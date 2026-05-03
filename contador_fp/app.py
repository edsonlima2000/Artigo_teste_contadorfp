import logging
import os
import time
import tkinter as tk
from tkinter import ttk

from .ai_client import AzureOpenAIAnalyzer
from .config import bootstrap
from .fp_service import FunctionPointService
from .gitlab_service import GitLabService


class ContadorSFPApp:
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title("CONTADOR DE PONTOS DE FUNCAO")

        self.gitlab_service = GitLabService(bootstrap())
        self.fp_service = FunctionPointService(self.gitlab_service, AzureOpenAIAnalyzer())

        self.project_var = tk.StringVar()
        self.issue_var = tk.StringVar()
        self.branch_var = tk.StringVar()
        self.merge_request_var = tk.StringVar()
        self.commit_var = tk.StringVar()

        self._build_ui()
        self._load_projects()

    def run(self):
        self.janela.mainloop()

    def _build_ui(self):
        tk.Label(self.janela, text="Selecione um Projeto:").grid(row=0, column=0, padx=10, pady=10)
        self.project_combobox = ttk.Combobox(self.janela, textvariable=self.project_var, width=80)
        self.project_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.project_combobox.bind("<<ComboboxSelected>>", self.update_issues)

        tk.Label(self.janela, text="Selecione uma Issue:").grid(row=1, column=0, padx=10, pady=10)
        self.issue_combobox = ttk.Combobox(self.janela, textvariable=self.issue_var, width=80)
        self.issue_combobox.grid(row=1, column=1, padx=10, pady=10)
        self.issue_combobox.bind("<<ComboboxSelected>>", self.update_branches_mrs)

        tk.Label(self.janela, text="Selecione um Branch:").grid(row=2, column=0, padx=10, pady=10)
        self.branch_combobox = ttk.Combobox(self.janela, textvariable=self.branch_var, width=80)
        self.branch_combobox.grid(row=2, column=1, padx=10, pady=10)
        self.branch_combobox.bind("<<ComboboxSelected>>", self.update_commits_branch)

        tk.Label(self.janela, text="Selecione um Merge Request:").grid(row=3, column=0, padx=10, pady=10)
        self.mr_combobox = ttk.Combobox(self.janela, textvariable=self.merge_request_var, width=80)
        self.mr_combobox.grid(row=3, column=1, padx=10, pady=10)
        self.mr_combobox.bind("<<ComboboxSelected>>", self.update_commits_mr)

        tk.Label(self.janela, text="Selecione um Commit:").grid(row=4, column=0, padx=10, pady=10)
        self.commit_combobox = ttk.Combobox(self.janela, textvariable=self.commit_var, width=80)
        self.commit_combobox.grid(row=4, column=1, padx=10, pady=10)

        self.tree = ttk.Treeview(
            self.janela,
            columns=("Nome_Arquivo", "Extensao", "Elemento_FP", "Pontos"),
            show="headings",
        )
        self.tree.heading("Nome_Arquivo", text="Nome do Arquivo")
        self.tree.heading("Extensao", text="Extensao")
        self.tree.heading("Elemento_FP", text="Elemento FP")
        self.tree.heading("Pontos", text="Pontos")
        self.tree.column("Nome_Arquivo", width=200)
        self.tree.column("Extensao", width=100)
        self.tree.column("Elemento_FP", width=150)
        self.tree.column("Pontos", width=50)
        self.tree.grid(row=5, columnspan=2, padx=10, pady=10)

        process_button = tk.Button(self.janela, text="Processar Selecao", command=self.process_selection)
        process_button.grid(row=6, columnspan=2, pady=20)

        self.output_label = tk.Label(self.janela, text="", fg="blue")
        self.output_label.grid(row=7, columnspan=2, pady=10)

    def _load_projects(self):
        projects = self.gitlab_service.get_projects()
        self.project_combobox["values"] = [f"{project.id}: {project.name}" for project in projects]

    def update_issues(self, *args):
        project = self.gitlab_service.get_project(self.project_var.get())

        self.issue_combobox["values"] = self.gitlab_service.get_issues(project)
        self.issue_var.set("N/A")

        self.branch_combobox["values"] = self.gitlab_service.get_branches(project)
        self.branch_var.set("N/A")

        self.mr_combobox["values"] = ["N/A"]
        self.merge_request_var.set("N/A")
        self.commit_combobox["values"] = ["N/A"]
        self.commit_var.set("N/A")

    def update_branches_mrs(self, *args):
        project = self.gitlab_service.get_project(self.project_var.get())
        jira_key = self._extract_jira_key(self.issue_var.get())

        self.branch_combobox["values"] = self.gitlab_service.get_branches(project, jira_key)
        self.branch_var.set("N/A")

        self.mr_combobox["values"] = self.gitlab_service.get_merge_requests(project, jira_key)
        self.merge_request_var.set("N/A")

        self.commit_combobox["values"] = self.gitlab_service.get_commits(project, jira_key=jira_key)
        self.commit_var.set("N/A")

    def update_commits_branch(self, *args):
        if self.branch_var.get() == "N/A":
            return

        self.merge_request_var.set("N/A")
        self.commit_var.set("N/A")
        self.commit_combobox["values"] = ["N/A"]
        self.output_label.config(text="Selecionando um branch, o merge request foi redefinido para 'N/A'.")

        project = self.gitlab_service.get_project(self.project_var.get())
        jira_key = self._extract_jira_key(self.issue_var.get())
        self.commit_combobox["values"] = self.gitlab_service.get_commits(
            project,
            branch_name=self.branch_var.get(),
            jira_key=jira_key,
        )
        self.commit_var.set("N/A")

    def update_commits_mr(self, *args):
        if self.merge_request_var.get() == "N/A":
            return

        self.branch_var.set("N/A")
        self.commit_var.set("N/A")
        self.commit_combobox["values"] = ["N/A"]

    def process_selection(self):
        selected_project = self.project_var.get()
        selected_branch = self.branch_var.get()
        selected_mr = self.merge_request_var.get()
        selected_commit_text = self.commit_var.get()

        if not selected_project:
            self.output_label.config(text="Erro: Selecione um projeto.")
            return

        project = self.gitlab_service.get_project(selected_project)

        if selected_branch != "N/A" and selected_mr != "N/A":
            self.output_label.config(text="Erro: Nao e possivel selecionar ambos, branch e merge request.")
            return

        metadata_info = self._metadata_info()
        if selected_mr != "N/A":
            resultado = self._process_merge_request(project, selected_mr, metadata_info)
        elif selected_branch != "N/A":
            resultado = self._process_branch_or_commit(project, selected_branch, selected_commit_text, metadata_info)
        else:
            self.output_label.config(text="Erro: Selecione um merge request, branch ou commit.")
            return

        if resultado.get("Erro"):
            self.output_label.config(text=resultado["Erro"])
            return

        self.preencher_grid(resultado.get("Elementos_FP", []))
        self.output_label.config(text=f"TOTAL GERAL DE SFP: {resultado.get('Total_SFP', 0)}")

    def _process_merge_request(self, project, selected_mr, metadata_info):
        mr_iid = selected_mr.split(":")[0]
        mr = project.mergerequests.get(mr_iid)
        return self.fp_service.process_fp_count(
            project,
            mr.source_branch,
            mr.target_branch,
            compare=True,
            metadata_info=metadata_info,
        )

    def _process_branch_or_commit(self, project, selected_branch, selected_commit_text, metadata_info):
        if selected_commit_text == "N/A":
            return self.fp_service.process_fp_count(
                project,
                selected_branch,
                None,
                compare=False,
                metadata_info=metadata_info,
            )

        selected_commit_id = self.gitlab_service.commit_map.get(selected_commit_text.split(":")[0])
        if not selected_commit_id:
            return {"Erro": "Erro: Commit selecionado nao encontrado."}

        return self.fp_service.process_fp_count_commit(project, selected_commit_id, metadata_info=metadata_info)

    def _metadata_info(self):
        return {
            "Timestamp_Inicio": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "Projeto": self.project_var.get(),
            "Issue": self.issue_var.get() if self.issue_var.get() != "N/A" else "N/A",
            "Branch": self.branch_var.get() if self.branch_var.get() != "N/A" else "N/A",
            "Merge_Request": self.merge_request_var.get() if self.merge_request_var.get() != "N/A" else "N/A",
            "Commit": self.commit_var.get() if self.commit_var.get() != "N/A" else "N/A",
        }

    def _extract_jira_key(self, selected_issue):
        if selected_issue == "N/A":
            return None
        issue_description = selected_issue.split(":")[1].strip()
        return issue_description.split()[0]

    def preencher_grid(self, elementos_fp):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in elementos_fp:
            try:
                nome_arquivo_completo = item.get("Nome_Arquivo", "Desconhecido")
                extensao = item.get("Extensao", "")
                if not extensao:
                    nome_arquivo, extensao = os.path.splitext(nome_arquivo_completo)
                    extensao = extensao.lstrip(".")
                else:
                    nome_arquivo = os.path.splitext(nome_arquivo_completo)[0]

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        nome_arquivo,
                        extensao.lstrip("."),
                        item.get("Elemento_FP", "Desconhecido"),
                        item.get("Pontos", 0),
                    ),
                )
            except KeyError as error:
                print(f"Erro ao preencher a grid, chave ausente: {error}")
                logging.error(f"Erro ao preencher a grid, chave ausente: {error}")


def main():
    ContadorSFPApp().run()
