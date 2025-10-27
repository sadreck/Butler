import pytest
from src.tests.helpers import _args_download, _get_db_path
from src.commands.download.command import CommandDownload
from src.database.database import Database
from src.libs.constants import GitHubRefType, RepoVisibility, PollStatus, RepoStatus, WorkflowType, WorkflowStatus
from src.tests.conftest import mock_handle_get_requests_download_vscode

@pytest.mark.parametrize('mock_requests_get', [mock_handle_get_requests_download_vscode], indirect=True)
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
