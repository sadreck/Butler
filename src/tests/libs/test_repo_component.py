from src.libs.components.repo import RepoComponent
from src.libs.exceptions import InvalidRepoFormat


def test_repo_component():
    try:
        repo = RepoComponent('')
        assert False
    except InvalidRepoFormat:
        assert True
    except Exception:
        assert False

    try:
        repo = RepoComponent('microsoft')
        assert False
    except InvalidRepoFormat:
        assert True
    except Exception:
        assert False

    repo = RepoComponent('microsoft/vscode')
    assert repo.name == 'vscode'
    assert repo.org.name == 'microsoft'
    assert repo.ref == ''

    repo = RepoComponent('microsoft/vscode@main')
    assert repo.name == 'vscode'
    assert repo.org.name == 'microsoft'
    assert repo.ref == 'main'

    repo = RepoComponent('microsoft/vscode/.github/workflows/ci.yaml@main')
    assert repo.name == 'vscode'
    assert repo.org.name == 'microsoft'
    assert repo.ref == 'main'

def test_repo_component_from_url():
    try:
        repo = RepoComponent('https://github.com/microsoft')
        assert False
    except InvalidRepoFormat:
        assert True
    except Exception:
        assert False

    repo = RepoComponent('https://github.com/microsoft/vscode')
    assert repo.name == 'vscode'
    assert repo.org.name == 'microsoft'
    assert repo.ref == ''

    repo = RepoComponent('https://github.com/microsoft/vscode/tree/v1')
    assert repo.name == 'vscode'
    assert repo.org.name == 'microsoft'
    assert repo.ref == 'v1'

    repo = RepoComponent('https://github.com/microsoft/vscode/tree/develop')
    assert repo.name == 'vscode'
    assert repo.org.name == 'microsoft'
    assert repo.ref == 'develop'

    repo = RepoComponent('https://github.com/microsoft/vscode/blob/main/.github/workflows/hello.yaml')
    assert repo.name == 'vscode'
    assert repo.org.name == 'microsoft'
    assert repo.ref == 'main'

    repo = RepoComponent('https://github.com/microsoft/vscode/tree/main/.github/actions/my-action')
    assert repo.name == 'vscode'
    assert repo.org.name == 'microsoft'
    assert repo.ref == 'main'

    repo = RepoComponent('https://github.com/microsoft/vscode/tree/main/resources/win32/bin')
    assert repo.name == 'vscode'
    assert repo.org.name == 'microsoft'
    assert repo.ref == 'main'

    try:
        repo = RepoComponent('https://example.com/microsoft/vscode')
        assert False
    except InvalidRepoFormat:
        assert True
    except Exception:
        assert False

def test_repo_component_from_docker():
    repo = RepoComponent('docker://microsoft/vs-action:v1')
    assert repo.name == 'vs-action'
    assert repo.org.name == 'microsoft'
    assert repo.ref == 'v1'

    repo = RepoComponent('docker://microsoft/vs-action')
    assert repo.name == 'vs-action'
    assert repo.org.name == 'microsoft'
    assert repo.ref == ''

    repo = RepoComponent('docker://php')
    assert repo.name == 'php'
    assert repo.org.name == '_'
    assert repo.ref == ''

    repo = RepoComponent('docker://php:8.1-cli')
    assert repo.name == 'php'
    assert repo.org.name == '_'
    assert repo.ref == '8.1-cli'

    repo = RepoComponent('docker://oskarstark/php-cs-fixer-ga:latest@sha256:ed1747b161640445dbbb41744a0c51b6e4e61af4e4bdc285242a6ad60e730dd')
    assert repo.name == 'php-cs-fixer-ga'
    assert repo.org.name == 'oskarstark'
    assert repo.ref == 'latest@sha256:ed1747b161640445dbbb41744a0c51b6e4e61af4e4bdc285242a6ad60e730dd'
