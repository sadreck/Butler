import pytest
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import RepoVisibility
from src.libs.utils import Utils
from src.tests.conftest import mock_handle_get_requests


@pytest.mark.parametrize('mock_requests_get', [mock_handle_get_requests], indirect=True)
def test_download(client, mock_requests_get):
    # action.yml
    component = WorkflowComponent('actions/checkout@v4')
    component.repo.visibility = RepoVisibility.PRIVATE
    contents = client.download_action(component)
    assert component.path == 'action.yml'
    assert Utils.md5(contents) == '4389e10539f7ee93066a83f50b76f946'

    # action.yaml
    component = WorkflowComponent('ossf/scorecard-action@main')
    component.repo.visibility = RepoVisibility.PRIVATE
    contents = client.download_action(component)
    assert component.path == 'action.yaml'
    assert Utils.md5(contents) == '9b70a3f3171b4ceb6851a6a074f65b09'

    # No action.
    component = WorkflowComponent('microsoft/vscode@main')
    component.repo.visibility = RepoVisibility.PRIVATE
    contents = client.download_action(component)
    assert component.path == ''
    assert contents is None
