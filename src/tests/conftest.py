import tempfile
import pytest
import os
from unittest.mock import patch
from src.database.database import Database
from src.github.client import GitHubClient
from src.libs.utils import Utils
from mock_responses import *

@pytest.fixture
def mock_requests_get(request):
    source = request.param

    def _side_effect(url, *args, **kwargs):
        match source.lower():
            case 'download_vscode':
                responses = download_vscode()
            case 'missing_org':
                responses = missing_org()
            case 'missing_repo':
                responses = missing_repo()
            case 'missing_workflow':
                responses = missing_workflow()
            case 'renamed_branch':
                responses = renamed_branch()
            case _:
                responses = default()

        url = url.replace('https://api.github.com', '')
        if not url in responses:
            raise ValueError(f"Unmocked URL: {url}")
        return responses[url].response()

    with patch('requests.get', side_effect=_side_effect):
        yield

@pytest.fixture
def logger():
    logger = Utils.init_logger(True, True)
    yield logger

@pytest.fixture
def client(logger):
    client = GitHubClient([os.getenv('GITHUB_TOKEN', '')], logger)
    yield client

@pytest.fixture
def database():
    db_file = os.path.join(tempfile.gettempdir(), 'tests.db')
    database = Database(db_file)

    yield database

    os.remove(db_file)
