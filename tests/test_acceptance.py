from contador_fp.fp_service import FunctionPointService
from contador_fp.gitlab_service import GitLabService
from tests.fakes.fake_gitlab import FakeBranch, FakeCommit, FakeGitLabClient, FakeProject
from tests.fakes.fake_openai import FakeAnalyzer


def test_acceptance_estimar_tamanho_funcional_por_branch():
    project = FakeProject(
        files={
            ("sha-main", "app.py"): "print('ok')",
            ("sha-main", "README.md"): "# doc",
        },
        branches=[FakeBranch("main", "sha-main")],
        commits=[FakeCommit("commit-1")],
    )
    analyzer = FakeAnalyzer(response={"Total_SFP": 5, "Elementos_FP": [{"Nome_Arquivo": "app.py", "Pontos": 5}]})
    service = FunctionPointService(GitLabService(FakeGitLabClient({1: project})), analyzer)

    result = service.process_fp_count(project, "main", compare=False)

    assert result["Total_SFP"] == 5
    assert result["Elementos_FP"] == [{"Nome_Arquivo": "app.py", "Pontos": 5}]
    assert analyzer.calls[0]["caminho_arquivo"] == "app.py"


def test_acceptance_ignorar_arquivos_inelegiveis():
    project = FakeProject(
        files={
            ("sha-main", "README.md"): "# doc",
            ("sha-main", "config.yaml"): "x: y",
        },
        branches=[FakeBranch("main", "sha-main")],
        commits=[FakeCommit("commit-1")],
    )
    analyzer = FakeAnalyzer()
    service = FunctionPointService(GitLabService(FakeGitLabClient({1: project})), analyzer)

    result = service.process_fp_count(project, "main", compare=False)

    assert result["Total_SFP"] == 0
    assert result["Elementos_FP"] == []
    assert analyzer.calls == []
