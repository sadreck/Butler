import pytest
from src.libs.components.repo import RepoComponent
from src.tests.conftest import mock_handle_get_requests


@pytest.mark.parametrize('mock_requests_get', [mock_handle_get_requests], indirect=True)
def test_repo(client, mock_requests_get):
    repo = RepoComponent('microsoft/vscode')

    result = client.get_repo(repo, False)
    assert isinstance(result, dict)
    assert result['name'] == repo.name

    result = client.get_repo(repo, True)
    assert isinstance(result, RepoComponent)
    assert result.name == repo.name
