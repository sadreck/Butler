import pytest
from src.libs.components.repo import RepoComponent
from src.libs.constants import RepoVisibility
from src.tests.conftest import mock_handle_get_requests


@pytest.mark.parametrize('mock_requests_get', [mock_handle_get_requests], indirect=True)
def test_tag_from_commit(client, mock_requests_get):
    component = RepoComponent('microsoft/vscode@main')
    component.visibility = RepoVisibility.PUBLIC
    tag = client.get_tag_from_commit(component, '6ae9c3600abba518f5930c5d054ce1a300273d4e')
    assert tag == 'translation/20170123.01'

@pytest.mark.parametrize('mock_requests_get', [mock_handle_get_requests], indirect=True)
def test_branch_from_commit(client, mock_requests_get):
    component = RepoComponent('microsoft/vscode@main')
    component.visibility = RepoVisibility.PUBLIC
    branch = client.get_branch_from_commit(component, '6b48a8557aede8df0cacd9ebe792f964b36780dd')
    assert branch == 'aamunger/backupSizeLimit'
