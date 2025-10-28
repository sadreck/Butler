import pytest
from src.github.exceptions import HttpNotFound


@pytest.mark.parametrize('mock_requests_get', ['default'], indirect=True)
def test_account_type(client, mock_requests_get):
    name = client.get_account_type('microsoft')
    assert name == 'organization'

    name = client.get_account_type('sadreck')
    assert name == 'user'

    try:
        name = client.get_account_type(f'does-not-exist-tests')
        assert False
    except HttpNotFound:
        assert True
    except Exception:
        assert False
