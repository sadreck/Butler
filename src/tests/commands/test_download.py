import pytest
from src.tests.helpers import _args_download, _get_db_path
from src.commands.download.command import CommandDownload
from src.database.database import Database
from src.libs.constants import GitHubRefType, RepoVisibility, PollStatus, RepoStatus, WorkflowType, WorkflowStatus

@pytest.mark.parametrize('mock_requests_get', ['download_vscode'], indirect=True)
def test_download_vscode(logger, mock_requests_get):
    command = CommandDownload(logger)

    output_database = _get_db_path()
    args = _args_download(repo=["microsoft/vscode"], database=output_database, very_verbose=True, workflow=['copilot-setup-steps.yml'])
    assert command.run(args) == True

    database = Database(output_database)

    assert database.orgs().count() == 2
    assert database.repos().count() == 4
    assert database.workflows().count() == 4
    assert database.jobs().count() == 0     # Not processed yet.
    assert database.steps().count() == 0    # Not processed yet.

    microsoft = database.orgs().find('microsoft')
    actions = database.orgs().find('actions')

    assert microsoft.id > 0
    assert actions.id > 0

    vscode = database.repos().find(microsoft.id, 'vscode', 'main')
    checkout = database.repos().find(actions.id, 'checkout', 'v5')

    assert vscode.id > 0
    assert vscode.ref_type == GitHubRefType.BRANCH
    assert vscode.ref_commit == '84fed05516884c03062782cd45adf04739c4ea04'
    assert vscode.resolved_ref == ''
    assert vscode.resolved_ref_type == GitHubRefType.UNKNOWN
    assert vscode.visibility == RepoVisibility.PUBLIC
    assert vscode.poll_status == PollStatus.SCANNED
    assert vscode.status == RepoStatus.OK
    assert vscode.stars == 177902
    assert vscode.fork == False
    assert vscode.archive == False

    assert checkout.id > 0
    assert checkout.ref_type == GitHubRefType.TAG
    assert checkout.ref_commit == '08c6903cd8c0fde910a37f88322edcfb5dd907a8'
    assert checkout.resolved_ref == ''
    assert checkout.resolved_ref_type == GitHubRefType.UNKNOWN
    assert checkout.visibility == RepoVisibility.PUBLIC
    assert checkout.poll_status == PollStatus.NONE
    assert checkout.status == RepoStatus.OK
    assert checkout.stars == 7166
    assert checkout.fork == False
    assert checkout.archive == False

    vscode_workflow = database.workflows().find(vscode.id, '.github/workflows/copilot-setup-steps.yml')
    checkout_workflow = database.workflows().find(checkout.id, 'action.yml')

    assert vscode_workflow.id > 0
    assert checkout_workflow.id > 0

    assert vscode_workflow.type == WorkflowType.WORKFLOW
    assert vscode_workflow.contents != ''
    assert vscode_workflow.data != ''
    assert vscode_workflow.status == WorkflowStatus.DOWNLOADED

    assert checkout_workflow.type == WorkflowType.ACTION
    assert checkout_workflow.contents != ''
    assert checkout_workflow.data != ''
    assert checkout_workflow.status == WorkflowStatus.DOWNLOADED

@pytest.mark.parametrize('mock_requests_get', ['missing_org'], indirect=True)
def test_download_missing_org(logger, mock_requests_get):
    command = CommandDownload(logger)

    output_database = _get_db_path()
    args = _args_download(repo=["microsoft-does-not-exist/vscode"], database=output_database, very_verbose=True)
    assert command.run(args) == True

    database = Database(output_database)

    assert database.orgs().count() == 1
    assert database.repos().count() == 1

    microsoft = database.orgs().find('microsoft-does-not-exist')
    assert microsoft.id > 0

    vscode = database.repos().find(microsoft.id, 'vscode', 'main')
    assert vscode is None

    vscode = database.repos().find(microsoft.id, 'vscode', None)
    assert vscode.id > 0
    assert vscode.status == RepoStatus.MISSING

@pytest.mark.parametrize('mock_requests_get', ['missing_repo'], indirect=True)
def test_download_missing_repo(logger, mock_requests_get):
    command = CommandDownload(logger)

    output_database = _get_db_path()
    args = _args_download(repo=["microsoft/vscode-does-not-exist"], database=output_database, very_verbose=True)
    assert command.run(args) == True

    database = Database(output_database)

    assert database.orgs().count() == 1
    assert database.repos().count() == 1

    microsoft = database.orgs().find('microsoft')
    assert microsoft.id > 0

    vscode = database.repos().find(microsoft.id, 'vscode-does-not-exist', None)
    assert vscode.id > 0
    assert vscode.status == RepoStatus.MISSING

@pytest.mark.parametrize('mock_requests_get', ['missing_workflow'], indirect=True)
def test_download_missing_workflow(logger, mock_requests_get):
    command = CommandDownload(logger)

    output_database = _get_db_path()
    args = _args_download(repo=["microsoft/vscode"], database=output_database, very_verbose=True, workflow=['does-not-exist.yaml'])
    assert command.run(args) == True

    database = Database(output_database)

    assert database.orgs().count() == 1
    assert database.repos().count() == 1
    assert database.workflows().count() == 0

    microsoft = database.orgs().find('microsoft')
    assert microsoft.id > 0

    vscode = database.repos().find(microsoft.id, 'vscode', 'main')
    assert vscode.id > 0

    assert vscode.status == RepoStatus.NO_WORKFLOWS

@pytest.mark.parametrize('mock_requests_get', ['renamed_branch'], indirect=True)
def test_download_renamed_branch(logger, mock_requests_get):
    command = CommandDownload(logger)

    output_database = _get_db_path()
    args = _args_download(repo=["apache/datafusion-ballista-python"], database=output_database, very_verbose=True, workflow=['comment_bot.yml'])
    assert command.run(args) == True

    database = Database(output_database)
    assert database.orgs().count() == 3

    r_lib = database.orgs().find('r-lib')
    assert r_lib.id > 0

    actions = database.repos().find(r_lib.id, 'actions', None)
    assert actions.id > 0
    assert actions.ref == 'old'
    assert actions.ref_commit == '2acb5b24ed4d2f8a065b600c903d5ee62bbbe893'
    assert actions.ref_old_name == 'master'
    assert actions.ref_type == GitHubRefType.BRANCH
    assert actions.status == RepoStatus.OK

    pr_fetch = database.workflows().find(actions.id, 'pr-fetch/action.yml')
    pr_push = database.workflows().find(actions.id, 'pr-push/action.yml')
    assert pr_fetch.id > 0
    assert pr_fetch.type == GitHubRefType.TAG
    assert pr_fetch.status == WorkflowStatus.DOWNLOADED

    assert pr_push.id > 0
    assert pr_push.type == GitHubRefType.TAG
    assert pr_push.status == WorkflowStatus.DOWNLOADED
