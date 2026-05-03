import pytest

from contador_fp.contracts import ContractError
from contador_fp.fp_service import FunctionPointService
from contador_fp.gitlab_service import GitLabService
from tests.fakes.fake_gitlab import FakeBranch, FakeCommit, FakeGitLabClient, FakeProject
from tests.fakes.fake_openai import FakeAnalyzer


def make_project():
    return FakeProject(
        files={
            ("sha-main", "app.py"): "print('ok')",
            ("sha-main", "README.md"): "# doc",
            ("sha-feature", "changed.py"): "print('changed')",
            ("commit-2", "changed.py"): "print('commit')",
        },
        branches=[
            FakeBranch("main", "sha-main"),
            FakeBranch("feature", "sha-feature"),
        ],
        commits=[
            FakeCommit("commit-2", title="Second", short_id="c2", parent_ids=["commit-1"]),
            FakeCommit("commit-1", title="First", short_id="c1"),
        ],
        comparisons={
            ("sha-main", "sha-feature"): [
                {"new_path": "changed.py"},
                {"new_path": "notes.md"},
            ],
            ("commit-1", "commit-2"): [
                {"new_path": "changed.py"},
            ],
        },
    )


def make_service(project, analyzer=None):
    gitlab_service = GitLabService(FakeGitLabClient({1: project}))
    return FunctionPointService(gitlab_service, analyzer or FakeAnalyzer())


def test_process_branch_filters_files_and_reads_by_resolved_sha():
    project = make_project()
    analyzer = FakeAnalyzer()
    service = make_service(project, analyzer)

    result = service.process_fp_count(project, "main", compare=False)

    assert result["Total_SFP"] == 3
    assert len(result["Elementos_FP"]) == 1
    assert len(analyzer.calls) == 1
    assert analyzer.calls[0]["caminho_arquivo"] == "app.py"
    assert project.files.refs_used == ["sha-main"]


def test_process_merge_request_uses_resolved_shas_for_compare_and_file_read():
    project = make_project()
    analyzer = FakeAnalyzer()
    service = make_service(project, analyzer)

    result = service.process_fp_count(project, "feature", "main", compare=True)

    assert result["Total_SFP"] == 3
    assert analyzer.calls[0]["caminho_arquivo"] == "changed.py"
    assert project.files.refs_used == ["sha-feature"]


def test_process_commit_uses_parent_diff():
    project = make_project()
    analyzer = FakeAnalyzer()
    service = make_service(project, analyzer)

    result = service.process_fp_count_commit(project, "commit-2")

    assert result["Total_SFP"] == 3
    assert analyzer.calls[0]["caminho_arquivo"] == "changed.py"
    assert project.files.refs_used == ["commit-2"]


def test_process_fp_count_requires_target_branch_when_compare_is_true():
    project = make_project()
    service = make_service(project)

    with pytest.raises(ContractError):
        service.process_fp_count(project, "feature", compare=True)


def test_invalid_ai_response_raises_contract_error_inside_file_processing():
    project = make_project()
    analyzer = FakeAnalyzer(response={"Total_SFP": "invalid", "Elementos_FP": []})
    service = make_service(project, analyzer)

    result = service.process_fp_count(project, "main", compare=False)

    assert result["Total_SFP"] == 0
    assert result["Elementos_FP"] == []
