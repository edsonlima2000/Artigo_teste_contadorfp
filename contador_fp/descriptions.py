from .config import SUPPORTED_EXTENSIONS


def is_supported_path(path):
    return any(path.endswith(extension) for extension in SUPPORTED_EXTENSIONS)


def gerar_descricao_projeto(files):
    descricao = "Descricao do Projeto: O sistema contem os seguintes componentes:\n"
    componentes = []

    for file in files:
        if file.get("type") == "blob" and is_supported_path(file["path"]):
            componentes.append(f"Arquivo: {file['path']} - Tipo: {file.get('type', 'desconhecido')}")

    if componentes:
        descricao += "\n".join(componentes)
    else:
        descricao += "Nenhum componente relevante encontrado.\n"

    descricao += "\n"
    return descricao


def gerar_descricao_detalhada(conteudo_arquivos):
    descricao_detalhada = "Descricao detalhada dos arquivos:\n"
    for path, content in conteudo_arquivos.items():
        descricao_detalhada += f"Arquivo: {path}\nConteudo:\n{content}\n"
    return descricao_detalhada
