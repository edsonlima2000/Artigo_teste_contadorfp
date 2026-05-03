import json
import logging

import gitlab

from .contracts import require, validate_ai_response
from .descriptions import gerar_descricao_detalhada, gerar_descricao_projeto, is_supported_path


class FunctionPointService:
    def __init__(self, gitlab_service, analyzer):
        self.gitlab_service = gitlab_service
        self.analyzer = analyzer

    def process_fp_count(self, project, source_branch, target_branch=None, compare=True, metadata_info=None):
        require(project is not None, "project e obrigatorio.")
        require(source_branch, "source_branch e obrigatorio.")
        if compare:
            require(target_branch, "target_branch e obrigatorio quando compare=True.")

        if not compare:
            return self._process_branch(project, source_branch, metadata_info)
        return self._process_branch_comparison(project, source_branch, target_branch)

    def process_fp_count_commit(self, project, selected_commit_id, metadata_info=None):
        require(project is not None, "project e obrigatorio.")
        require(selected_commit_id, "selected_commit_id e obrigatorio.")
        print("Processando contagem de Function Points para o commit selecionado...")

        previous_commit = self.gitlab_service.get_previous_commit(project, selected_commit_id)
        if previous_commit:
            diffs = self.gitlab_service.get_diff_between_commits(project, previous_commit.id, selected_commit_id)
        else:
            commit = project.commits.get(selected_commit_id)
            diffs = commit.diff()

        resultado_total = {"Total_SFP": 0, "Elementos_FP": [], "Metadata": metadata_info}
        self._process_diffs(project, diffs, selected_commit_id, resultado_total)
        return resultado_total

    def _process_branch(self, project, source_branch, metadata_info):
        source_ref = self.gitlab_service.resolve_branch_sha(project, source_branch)
        print(f"Processando todos os arquivos no branch {source_branch} ({source_ref})...")
        files = project.repository_tree(ref=source_ref, recursive=True)
        resultado_total = {"Total_SFP": 0, "Elementos_FP": [], "Metadata": metadata_info}

        with open("resultado_intermediario.txt", "w") as resultado_intermediario:
            for file in files:
                path = file["path"]
                if not is_supported_path(path):
                    logging.info(f"Ignorando arquivo {path} - Extensao nao suportada")
                    continue

                logging.info(f"Processando arquivo {path} no branch {source_branch} ({source_ref})")
                try:
                    file_content = project.files.get(file_path=path, ref=source_ref).decode().decode("utf-8")
                except gitlab.exceptions.GitlabGetError as error:
                    logging.error(f"Erro ao obter o arquivo {path} no branch {source_branch} ({source_ref}): {error}")
                    continue

                self._analyze_file(
                    resultado_intermediario,
                    resultado_total,
                    f"Arquivo {path} no branch {source_branch}",
                    path,
                    file_content,
                )

        return resultado_total

    def _process_branch_comparison(self, project, source_branch, target_branch):
        source_ref = self.gitlab_service.resolve_branch_sha(project, source_branch)
        target_ref = self.gitlab_service.resolve_branch_sha(project, target_branch)
        print(f"Comparando {source_branch} ({source_ref}) com {target_branch} ({target_ref})...")
        resultado_total = {"Total_SFP": 0, "Elementos_FP": []}

        try:
            comparison = project.repository_compare(from_=target_ref, to=source_ref)
            diffs = comparison["diffs"]
        except Exception as error:
            print(f"Erro ao comparar os branches: {error}")
            logging.error(f"Erro ao comparar os branches: {error}")
            resultado_total["Erro"] = "Erro ao comparar os branches."
            return resultado_total

        self._process_diffs(project, diffs, source_ref, resultado_total)
        return resultado_total

    def _process_diffs(self, project, diffs, ref, resultado_total):
        with open("resultado_intermediario.txt", "w") as resultado_intermediario:
            for diff in diffs:
                path = diff.get("new_path") or diff.get("old_path")
                if not path or not is_supported_path(path):
                    logging.info(f"Ignorando arquivo {path} - Extensao nao suportada")
                    continue

                logging.info(f"Processando arquivo {path} na referencia {ref}")
                try:
                    file_content = project.files.get(file_path=path, ref=ref).decode().decode("utf-8")
                except gitlab.exceptions.GitlabGetError as error:
                    logging.error(f"Erro ao obter o arquivo {path} na referencia {ref}: {error}")
                    continue

                self._analyze_file(
                    resultado_intermediario,
                    resultado_total,
                    f"Alteracoes no arquivo {path}",
                    path,
                    file_content,
                )

    def _analyze_file(self, resultado_intermediario, resultado_total, descricao_contexto, path, file_content):
        conteudo_arquivos = {path: file_content}
        descricao_detalhada = gerar_descricao_detalhada(conteudo_arquivos)
        descricao_projeto = gerar_descricao_projeto([{"path": path, "type": "blob"}])

        try:
            resposta = validate_ai_response(self.analyzer.consultar_especialista_ai(
                descricao_contexto,
                descricao_detalhada,
                path,
            ))
            if resposta:
                resultado_total["Total_SFP"] += resposta.get("Total_SFP", 0)
                resultado_total["Elementos_FP"].extend(resposta.get("Elementos_FP", []))
                resultado_intermediario.write(json.dumps(resposta) + "\n")
        except Exception as error:
            logging.error(f"Erro ao processar o arquivo {path}: {error}")
