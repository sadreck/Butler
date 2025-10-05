import copy

from src.database.database import Database
from src.libs.components.org import OrgComponent
from src.libs.components.repo import RepoComponent
from src.libs.constants import RepoVisibility, GitHubRefType, RepoStatus, PollStatus
from src.libs.exceptions import MissingComponentDetails


def test_db_repos(database: Database) -> None:
    # Create an org.
    org_component = OrgComponent('microsoft')
    repo_component = RepoComponent('microsoft/vscode')
    microsoft = database.orgs().create(org_component)
    assert microsoft.name == 'microsoft'

    try:
        repo = database.repos().create(repo_component)
        assert False
    except MissingComponentDetails:
        assert True
    except Exception:
        assert False

    repo_component.org.id = microsoft.id
    repo_component.visibility = RepoVisibility.PUBLIC
    repo_component.ref_type = GitHubRefType.BRANCH
    repo_component.commit = 'abcdefg'
    repo_component.status = RepoStatus.OK
    repo_component.visibility = RepoVisibility.PUBLIC

    vscode = database.repos().create(repo_component)
    assert vscode.id == 1
    assert vscode.org_id == microsoft.id
    assert vscode.name == repo_component.name
    assert vscode.ref == repo_component.ref
    assert vscode.ref_type == repo_component.ref_type
    assert vscode.ref_commit == repo_component.ref_commit
    assert vscode.status == repo_component.status
    assert vscode.poll_status == PollStatus.NONE
    assert vscode.visibility == repo_component.visibility

    vscode1 = database.repos().get(vscode.id)
    assert vscode.id == vscode1.id

    vscode1 = database.repos().get(microsoft.id)
    assert vscode.id == vscode1.id

    vscode1 = database.repos().find(microsoft.id, 'VSCODE', None)
    assert vscode.id == vscode1.id

    # Try to get vscode but with a different branch.
    vscode1 = database.repos().find(microsoft.id, 'vscode', 'develop')
    assert vscode1 is None

    # Create it.
    component1 = copy.deepcopy(repo_component)
    component1.ref = 'develop'
    vscode1 = database.repos().create(component1)
    assert vscode1.id == 2
    assert vscode1.ref == 'develop'

    database.repos().set_poll_status(vscode.id, PollStatus.SCANNED)
    database.repos().set_status(vscode.id, RepoStatus.MISSING)

    database.refresh_record(vscode)
    assert vscode.poll_status == PollStatus.SCANNED
    assert vscode.status == RepoStatus.MISSING
