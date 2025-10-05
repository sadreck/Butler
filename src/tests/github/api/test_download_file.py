import pytest
from src.github.exceptions import ErrorDownloadingFile
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import RepoVisibility
from src.libs.utils import Utils
from src.tests.conftest import mock_handle_get_requests


@pytest.mark.parametrize('mock_requests_get', [mock_handle_get_requests], indirect=True)
def test_download(client, mock_requests_get):
    component = WorkflowComponent('microsoft/vscode/.github/workflows/telemetry.yml@main')
    component.repo.visibility = RepoVisibility.PUBLIC
    contents = client.download(component)
    assert Utils.md5(contents) == 'd15c6511dde0a200680ee5ff35a128d0'

    # Switch to an authenticated call
    component.repo.visibility = RepoVisibility.PRIVATE
    contents = client.download(component)
    assert Utils.md5(contents) == 'd15c6511dde0a200680ee5ff35a128d0'

    try:
        # Download a file that does not exist.
        component = WorkflowComponent('microsoft/vscode/.github/workflows/telemetry-does-not-exist.yml@main')
        component.repo.visibility = RepoVisibility.PUBLIC
        contents = client.download(component)
        assert False
    except ErrorDownloadingFile:
        assert True
    except Exception:
        assert False
