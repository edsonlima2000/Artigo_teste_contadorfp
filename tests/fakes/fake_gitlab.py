class FakeFileContent:
    def __init__(self, content):
        self.content = content

    def decode(self):
        return self.content.encode("utf-8")


class FakeFileStore:
    def __init__(self, files):
        self.files = files
        self.refs_used = []

    def get(self, file_path, ref):
        self.refs_used.append(ref)
        key = (ref, file_path)
        if key not in self.files:
            raise RuntimeError(f"Arquivo nao encontrado: {file_path}@{ref}")
        return FakeFileContent(self.files[key])


class FakeBranch:
    def __init__(self, name, commit_id):
        self.name = name
        self.commit = {"id": commit_id}


class FakeBranchStore:
    def __init__(self, branches):
        self.branches = {branch.name: branch for branch in branches}

    def list(self, all=True):
        return list(self.branches.values())

    def get(self, branch_name):
        return self.branches[branch_name]


class FakeCommit:
    def __init__(self, commit_id, title="Commit", short_id=None, parent_ids=None, diffs=None):
        self.id = commit_id
        self.title = title
        self.short_id = short_id or commit_id[:8]
        self.parent_ids = parent_ids or []
        self._diffs = diffs or []

    def diff(self):
        return self._diffs


class FakeCommitStore:
    def __init__(self, commits):
        self.commits = {commit.id: commit for commit in commits}
        self.commit_list = commits

    def list(self, ref_name=None, all=True):
        return self.commit_list

    def get(self, commit_id):
        return self.commits[commit_id]


class FakeMergeRequest:
    def __init__(self, iid, title, source_branch, target_branch, commits=None):
        self.iid = iid
        self.title = title
        self.source_branch = source_branch
        self.target_branch = target_branch
        self._commits = commits or []

    def commits(self):
        return self._commits


class FakeMergeRequestStore:
    def __init__(self, merge_requests):
        self.merge_requests = {str(mr.iid): mr for mr in merge_requests}

    def list(self, all=True):
        return list(self.merge_requests.values())

    def get(self, mr_iid):
        return self.merge_requests[str(mr_iid)]


class FakeIssue:
    def __init__(self, iid, title):
        self.iid = iid
        self.title = title


class FakeIssueStore:
    def __init__(self, issues):
        self.issues = issues

    def list(self, all=True):
        return self.issues


class FakeProject:
    def __init__(self, files, branches, commits, merge_requests=None, issues=None, comparisons=None):
        self.files = FakeFileStore(files)
        self.branches = FakeBranchStore(branches)
        self.commits = FakeCommitStore(commits)
        self.mergerequests = FakeMergeRequestStore(merge_requests or [])
        self.issues = FakeIssueStore(issues or [])
        self.comparisons = comparisons or {}
        self.default_branch = "main"

    def repository_tree(self, ref, recursive=True):
        paths = []
        for file_ref, path in self.files.files:
            if file_ref == ref:
                paths.append({"path": path, "type": "blob"})
        return paths

    def repository_compare(self, from_, to):
        return {"diffs": self.comparisons.get((from_, to), [])}


class FakeProjectStore:
    def __init__(self, projects):
        self.projects = projects

    def get(self, project_id):
        return self.projects[int(project_id)]

    def list(self, owned=True, all=True):
        return list(self.projects.values())


class FakeGitLabClient:
    def __init__(self, projects):
        self.projects = FakeProjectStore(projects)
