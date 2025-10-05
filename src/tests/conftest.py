import tempfile
import pytest
import os
from unittest.mock import patch
from src.database.database import Database
from src.github.client import GitHubClient
from src.libs.utils import Utils
from src.tests.mock_response import MockResponse


@pytest.fixture
def mock_requests_get(request):
    with patch('requests.get', side_effect=request.param):
        yield

@pytest.fixture
def logger():
    logger = Utils.init_logger(True, True)
    yield logger

@pytest.fixture
def client(logger):
    client = GitHubClient([os.getenv('GITHUB_TOKEN', '')], logger)
    yield client

def github_responses() -> dict:
    return {
        '/rate_limit': MockResponse('rate_limit.json', None, 200),
        '/users/microsoft': MockResponse('accounts/microsoft.json', None, 200),
        '/users/sadreck': MockResponse('accounts/sadreck.json', None, 200),
        '/users/does-not-exist-tests': MockResponse('accounts/does-not-exist-tests.json', None, 404),
        '/repos/microsoft/vscode': MockResponse('microsoft/fulfillment-vscode.json', None, 200),
        '/repos/microsoft/vscode/git/ref/heads/main': MockResponse('microsoft/fulfillment-vscode-ref-heads-main.json', None, 200),
        '/repos/microsoft/vscode/git/ref/tags/1.100.0': MockResponse('microsoft/fulfillment-vscode-ref-tags-1.100.0.json', None, 200),
        '/repos/microsoft/vscode/commits/19c72e4d24fe4ac9a7fc7b8161a3a852246282a2': MockResponse('microsoft/fulfillment-vscode-ref-commits-19c72e4d.json', None, 200),
        '/repos/microsoft/vscode/git/ref/heads/1.100.0': MockResponse('microsoft/fulfillment-vscode-ref-heads-1.100.0.json', None, 404),
        '/repos/microsoft/vscode/git/ref/heads/19c72e4d24fe4ac9a7fc7b8161a3a852246282a2': MockResponse('microsoft/fulfillment-vscode-ref-heads-19c72e4d.json', None, 404),
        '/repos/microsoft/vscode/git/ref/tags/19c72e4d24fe4ac9a7fc7b8161a3a852246282a2': MockResponse('microsoft/fulfillment-vscode-ref-tags-19c72e4d.json', None, 404),
        '/repos/aws-actions/configure-aws-credentials': MockResponse('aws-actions/repo-aws-creds.json', None, 200),
        '/repos/aws-actions/configure-aws-credentials/commits/5579c002bb4778aa43395ef1df492868a9a1c83f': MockResponse('aws-actions/fulfillment-aws-creds-commits.json', None, 422),
        '/repos/aws-actions/configure-aws-credentials/git/ref/heads/5579c002bb4778aa43395ef1df492868a9a1c83f': MockResponse('aws-actions/fulfillment-aws-creds-ref-heads.json', None, 404),
        '/repos/aws-actions/configure-aws-credentials/git/ref/tags/5579c002bb4778aa43395ef1df492868a9a1c83f': MockResponse('aws-actions/fulfillment-aws-creds-ref-tags.json', None, 404),
        '/repos/aws-actions/configure-aws-credentials/git/tags/5579c002bb4778aa43395ef1df492868a9a1c83f': MockResponse('aws-actions/fulfillment-aws-creds-git-tags.json', None, 200),
        '/orgs/microsoft/repos': MockResponse('microsoft/microsoft-page-1-contents.json', 'microsoft/microsoft-page-1-headers.json', 200),
        '/organizations/6154722/repos?per_page=10&sort=full_name&page=2': MockResponse('microsoft/microsoft-page-2-contents.json', 'microsoft/microsoft-page-2-headers.json', 200),
        '/organizations/6154722/repos?per_page=10&sort=full_name&page=3': MockResponse('microsoft/microsoft-page-3-contents.json', None, 200),
        '/repos/microsoft/vscode/contents/.github/workflows': MockResponse('microsoft/vscode-ls-workflows.json', None, 200),
        '/repos/microsoft/vscode/contents/.github/workflows-meh': MockResponse('microsoft/vscode-ls-workflows-not-found.json', None, 404),
        'https://raw.githubusercontent.com/microsoft/vscode/main/.github/workflows/telemetry.yml': MockResponse('microsoft/file-vscode-telemetry.yml', None, 200, is_json_contents=False),
        '/repos/microsoft/vscode/contents/.github/workflows/telemetry.yml?ref=main': MockResponse('microsoft/file-vscode-telemetry.json', None, 200),
        'https://raw.githubusercontent.com/microsoft/vscode/main/.github/workflows/telemetry-does-not-exist.yml': MockResponse('microsoft/file-vscode-telemetry-does-not-exist.json', None, 404),
        '/repos/actions/checkout/contents/action.yml?ref=v4': MockResponse('actions/checkout-v4.json', None, 200),
        '/repos/ossf/scorecard-action/contents/action.yml?ref=main': MockResponse('ossf/scorecard-action-404.json', None, 404),
        '/repos/ossf/scorecard-action/contents/action.yaml?ref=main': MockResponse('ossf/scorecard-action-main.json', None, 200),
        '/repos/microsoft/vscode/contents/action.yml?ref=main': MockResponse('microsoft/action-yml-404.json', None, 404),
        '/repos/microsoft/vscode/contents/action.yaml?ref=main': MockResponse('microsoft/action-yaml-404.json', None, 404),
        '/repos/microsoft/vscode/contents/Dockerfile?ref=main': MockResponse('microsoft/action-yaml-404.json', None, 404),
        '/repos/spotify/beam/contents/.github/actions/cancel-workflow-runs': MockResponse('spotify/beam-action.json', None, 200),
        '/repos/microsoft/vscode/tags': MockResponse('microsoft/tags-page-1.json', 'microsoft/tags-page-1-headers.json', 200),
        '/repositories/41881900/tags?per_page=10&page=2': MockResponse('microsoft/tags-page-2.json', None, 200),
        '/repos/microsoft/vscode/branches': MockResponse('microsoft/branches-page-1.json', 'microsoft/branches-page-1-headers.json', 200),
        '/repositories/41881900/branches?per_page=10&page=2': MockResponse('microsoft/branches-page-2.json', None, 200)
    }

def mock_handle_get_requests(url, *args, **kwargs):
    responses = github_responses()
    url = url.replace('https://api.github.com', '')
    if not url in responses:
        raise ValueError(f"Unmocked URL: {url}")
    return responses[url].response()

@pytest.fixture
def database():
    db_file = os.path.join(tempfile.gettempdir(), 'tests.sqlite3')
    database = Database(db_file)

    yield database

    os.remove(db_file)
