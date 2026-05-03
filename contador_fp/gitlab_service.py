class GitLabService:
    def __init__(self, client):
        self.client = client
        self.commit_map = {}

    def get_project(self, project_text):
        project_id = int(project_text.split(":")[0])
        return self.client.projects.get(project_id)

    def get_projects(self):
        print("Obtendo projetos...")
        return self.client.projects.list(owned=True, all=True)

    def get_issues(self, project):
        issues = project.issues.list(all=True)
        return ["N/A"] + [f"{issue.iid}: {issue.title}" for issue in issues]

    def get_branches(self, project, jira_key=None):
        branches = project.branches.list(all=True)
        branch_list = ["N/A"]
        for branch in branches:
            if jira_key:
                if jira_key.lower() in branch.name.lower():
                    branch_list.append(branch.name)
            else:
                branch_list.append(branch.name)
        return branch_list

    def get_merge_requests(self, project, jira_key=None):
        merge_requests = project.mergerequests.list(all=True)
        mr_list = ["N/A"]
        for mr in merge_requests:
            if jira_key:
                if jira_key.lower() in mr.title.lower():
                    mr_list.append(f"{mr.iid}: {mr.title}")
            else:
                mr_list.append(f"{mr.iid}: {mr.title}")
        return mr_list

    def get_commits(self, project, branch_name=None, mr_iid=None, jira_key=None):
        if branch_name and branch_name != "N/A":
            commits = project.commits.list(ref_name=branch_name, all=True)
        elif mr_iid and mr_iid != "N/A":
            mr = project.mergerequests.get(mr_iid)
            commits = mr.commits()
        else:
            commits = project.commits.list(all=True)

        commit_list = ["N/A"]
        for commit in commits:
            if jira_key:
                if jira_key.lower() in commit.title.lower():
                    self.commit_map[commit.short_id] = commit.id
                    commit_list.append(f"{commit.short_id}: {commit.title}")
            else:
                self.commit_map[commit.short_id] = commit.id
                commit_list.append(f"{commit.short_id}: {commit.title}")
        return commit_list

    def get_previous_commit(self, project, commit_id):
        commit = project.commits.get(commit_id)
        parent_ids = getattr(commit, "parent_ids", None)
        if parent_ids:
            return project.commits.get(parent_ids[0])

        default_branch = getattr(project, "default_branch", None) or "master"
        commits = project.commits.list(ref_name=default_branch, all=True)
        for index, commit in enumerate(commits):
            if commit.id.strip() == commit_id.strip():
                return commits[index + 1] if index + 1 < len(commits) else None
        return None

    def get_diff_between_commits(self, project, from_commit_id, to_commit_id):
        comparison = project.repository_compare(from_commit_id, to_commit_id)
        return comparison["diffs"]

    def resolve_branch_sha(self, project, branch_name):
        branch = project.branches.get(branch_name)
        commit = getattr(branch, "commit", None)

        if isinstance(commit, dict):
            return commit.get("id") or commit.get("sha")

        commit_id = getattr(commit, "id", None)
        if commit_id:
            return commit_id

        raise ValueError(f"Nao foi possivel resolver SHA do branch {branch_name}.")
