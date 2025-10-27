import pytest
from src.github.exceptions import HttpNotFound
from src.libs.components.repo import RepoComponent


@pytest.mark.parametrize('mock_requests_get', ['default'], indirect=True)
def test_ls(client, mock_requests_get):
    repo = RepoComponent('microsoft/vscode')
    files = client.ls(repo, '.github/workflows')

    expected_files = [
        '.github/workflows/basic.yml', '.github/workflows/check-clean-git-state.sh',
        '.github/workflows/ci.yml', '.github/workflows/monaco-editor.yml',
        '.github/workflows/no-package-lock-changes.yml', '.github/workflows/no-yarn-lock-changes.yml',
        '.github/workflows/rich-navigation.yml.off', '.github/workflows/telemetry.yml'
    ]
    for file in files:
        if file in expected_files:
            expected_files.remove(file)

    assert len(expected_files) == 0

@pytest.mark.parametrize('mock_requests_get', ['default'], indirect=True)
def test_ls_inexistent(client, mock_requests_get):
    repo = RepoComponent('microsoft/vscode')
    try:
        files = client.ls(repo, '.github/workflows-meh')
        assert False
    except HttpNotFound as e:
        assert True
    except Exception:
        assert False
