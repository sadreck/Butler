import pytest
from src.tests.helpers import _args_download, _args_process, _get_db_path
from src.commands.download.command import CommandDownload
from src.commands.process.command import CommandProcess
from src.database.database import Database
from src.tests.conftest import mock_handle_get_requests_download_vscode

@pytest.mark.parametrize('mock_requests_get', [mock_handle_get_requests_download_vscode], indirect=True)
def test_process_vscode(logger, mock_requests_get):
    command = CommandDownload(logger)

    output_database = _get_db_path()
    args = _args_download(repo=["microsoft/vscode"], database=output_database, very_verbose=True, workflow=['copilot-setup-steps.yml'])
    assert command.run(args) == True

    command = CommandProcess(logger)
    args = _args_process(database=output_database)
    assert command.run(args) == True

    database = Database(output_database)

    assert database.jobs().count() == 4
    assert database.steps().count() == 14
    assert database.jobs().jobdata_count() == 143
    assert database.steps().stepdata_count() == 50
    assert database.workflows().workflowdata_count() == 7

    microsoft = database.orgs().find('microsoft')
    vscode = database.repos().find(microsoft.id, 'vscode', 'main')
    vscode_workflow = database.workflows().find(microsoft.id, '.github/workflows/copilot-setup-steps.yml')

    workflow_name = database.select("SELECT * FROM workflow_data WHERE property = 'name' AND workflow_id = :id", {'id': vscode_workflow.id})
    assert len(workflow_name) == 1
    assert workflow_name[0]['value'] == 'Copilot Setup Steps'

    workflow_on = database.select("SELECT * FROM workflow_data WHERE property = 'on' AND workflow_id = :id ORDER BY value", {'id': vscode_workflow.id})
    assert len(workflow_on) == 3
    assert workflow_on[0]['value'] == 'pull_request'
    assert workflow_on[1]['value'] == 'push'
    assert workflow_on[2]['value'] == 'workflow_dispatch'

    jobs = database.select("SELECT * FROM jobs WHERE workflow_id = :id", {'id': vscode_workflow.id})
    assert len(jobs) == 1
    assert jobs[0]['shortname'] == 'copilot-setup-steps'

    job_data = database.select("SELECT * FROM job_data WHERE job_id = :id ORDER BY property", {'id': jobs[0]['id']})
    assert len(job_data) == 3
    assert job_data[0]['property'] == 'permissions' and job_data[0]['name'] == 'contents' and job_data[0]['value'] == 'read'
    assert job_data[1]['property'] == 'runner' and job_data[1]['value'] == 'vscode-large-runners'
    assert job_data[2]['property'] == 'runs-on' and job_data[2]['value'] == 'vscode-large-runners'

    step_data = database.select("SELECT * FROM step_data WHERE property = 'name' ORDER BY step_id, property, name")
    assert len(step_data) == 14
    step_names = [
        'Checkout microsoft/vscode',
        'Setup Node.js',
        'Setup system services',
        'Prepare node_modules cache key',
        'Restore node_modules cache',
        'Extract node_modules cache',
        'Install build dependencies',
        'Install dependencies',
        'Create node_modules archive',
        'Create .build folder',
        'Prepare built-in extensions cache key',
        'Restore built-in extensions cache',
        'Download built-in extensions',
        'Download Electron and Playwright'
    ]
    for i, name in enumerate(step_data):
        assert step_data[i]['value'] == step_names[i]

    sql = """
        SELECT
            v.id,
            sd.property,
            sd.name,
            sd.value
        FROM variables v
        JOIN step_data sd ON sd.id = v.step_data_id AND v.step_data_id > 0
        JOIN steps s ON s.id = sd.step_id
        WHERE
            s.step_number = 8
        ORDER BY sd.name, sd.value
    """
    results = database.select(sql)
    data = [
        {'property': 'env', 'name': 'ELECTRON_SKIP_BINARY_DOWNLOAD', 'value': '1'},
        {'property': 'env', 'name': 'GITHUB_TOKEN', 'value': '${{ secrets.GITHUB_TOKEN }}'},
        {'property': 'env', 'name': 'GITHUB_TOKEN', 'value': '${{ secrets.GITHUB_TOKEN }}'},
        {'property': 'env', 'name': 'PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD', 'value': '1'},
        {'property': 'env', 'name': 'VSCODE_ARCH', 'value': 'x64'},
        {'property': 'env', 'name': 'npm_config_arch', 'value': 'x64'},
    ]
    for i, result in enumerate(results):
        assert result['property'] == data[i]['property']
        assert result['name'] == data[i]['name']
        assert result['value'] == data[i]['value']
