from contador_fp.descriptions import gerar_descricao_detalhada, gerar_descricao_projeto, is_supported_path


def test_is_supported_path_accepts_code_extensions():
    assert is_supported_path("src/app.py")
    assert is_supported_path("web/index.jsp")
    assert is_supported_path("script.ts")


def test_is_supported_path_rejects_non_code_extensions():
    assert not is_supported_path("README.md")
    assert not is_supported_path("config.yaml")
    assert not is_supported_path("")


def test_gerar_descricao_projeto_keeps_only_supported_files():
    descricao = gerar_descricao_projeto(
        [
            {"path": "src/app.py", "type": "blob"},
            {"path": "README.md", "type": "blob"},
        ]
    )

    assert "src/app.py" in descricao
    assert "README.md" not in descricao


def test_gerar_descricao_detalhada_preserves_path_and_content():
    descricao = gerar_descricao_detalhada({"src/app.py": "print('ok')"})

    assert "src/app.py" in descricao
    assert "print('ok')" in descricao
