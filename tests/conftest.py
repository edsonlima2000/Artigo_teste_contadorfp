import os

import pytest


@pytest.fixture(autouse=True)
def isolated_workdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "prompt.txt").write_text("{{descricao_projeto}}\n{{descricao_detalhada}}", encoding="utf-8")
    os.environ["AZURE_OPENAI_TAMANHO_BLOCO"] = "12000"
    os.environ["AZURE_OPENAI_MAX_RETRIES"] = "1"
    os.environ["AZURE_OPENAI_RETRY_DELAY"] = "0"
    return tmp_path
