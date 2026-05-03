from contador_fp.gitlab_service import GitLabService
from tests.fakes.fake_gitlab import FakeBranch, FakeCommit, FakeGitLabClient, FakeProject


def make_service_and_project():
    project = FakeProject(
        files={("sha-main", "app.py"): "print('ok')"},
        branches=[FakeBranch("main", "sha-main")],
        commits=[
            FakeCommit("commit-2", title="Second", short_id="c2", parent_ids=["commit-1"]),
            FakeCommit("commit-1", title="First", short_id="c1"),
        ],
    )
    client = FakeGitLabClient({1: project})
    return GitLabService(client), project


def test_get_commits_populates_commit_map():
    service, project = make_service_and_project()

    commits = service.get_commits(project, branch_name="main")

    assert commits == ["N/A", "c2: Second", "c1: First"]
    assert service.commit_map["c2"] == "commit-2"
    assert service.commit_map["c1"] == "commit-1"


def test_get_previous_commit_uses_parent_id_first():
    service, project = make_service_and_project()

    previous = service.get_previous_commit(project, "commit-2")

    assert previous.id == "commit-1"


def test_resolve_branch_sha_returns_branch_commit_id():
    service, project = make_service_and_project()

    assert service.resolve_branch_sha(project, "main") == "sha-main"
