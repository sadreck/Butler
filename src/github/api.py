from json import JSONDecodeError
import requests
import time
import jwt
from loguru import logger
from requests.models import Response
from src.github.api_helper import GitHubApiHelper
from src.github.exceptions import (
    ApiRateLimitExceeded, HttpAccessBlocked, HttpEmptyRepo,
    HttpNotFound, HttpNoCommitFound, HttpInvalidState,
    HttpInvalidRequest, HttpTooManyRequests, HttpUnknownError
)
from src.github.token_manager import TokenManager


class GitHubApi(GitHubApiHelper):
    _token_manager: TokenManager = None
    _api_endpoint: str = 'https://api.github.com'
    _total_requests: int = 0
    log: logger = None

    @property
    def token_manager(self) -> TokenManager:
        return self._token_manager

    def __init__(self, access_tokens: list[str], log: logger):
        self.log = log
        self._token_manager = TokenManager(access_tokens, log)
        self._load_debug()

    def _increase_request_counter(self) -> None:
        self._total_requests += 1

    @property
    def total_requests(self) -> int:
        return self._total_requests

    def _endpoint(self, url: str) -> str:
        if not url.startswith('/'):
            return url
        return self._api_endpoint.rstrip('/') + '/' + url.lstrip('/')

    def _headers(self, authenticated: bool, additional_headers: dict | None) -> dict[str, str]:
        headers = {}
        if authenticated:
            headers = {
                'Authorization': f"token {self.token_manager.instance().access_token}",
                'Accept': 'application/vnd.github.v3+json'
            }

        if isinstance(additional_headers, dict):
            headers.update(additional_headers)

        return headers

    def get(self, url: str, params: dict | None = None, additional_headers: dict | None = None, response_headers: dict | None = None, authenticated: bool = True, is_retry: bool = False, return_raw: bool = False) -> dict | list | str:
        headers = self._headers(authenticated, additional_headers)
        endpoint = self._endpoint(url)

        try:
            self._increase_request_counter()
            response = requests.get(endpoint, params=params, headers=headers, timeout=(5, None))
        except Exception as e:
            self.log.error(f"Error while getting {url}: {e}")
            self.log.warning(f"Trying to fetch {url} again")
            # Try again, could be a random connection error.
            self._increase_request_counter()
            response = requests.get(endpoint, params=params, headers=headers, timeout=(5, None))

        self._save_debug(url, params, additional_headers, authenticated, response)

        if self._is_api_rate_limit_error(response):
            if is_retry:
                raise ApiRateLimitExceeded()
            # Refresh API keys and try again.
            self.refresh_tokens()
            return self.get(url, params, additional_headers, response_headers, authenticated, True)

        # Return by reference.
        if response_headers is not None:
            response_headers = response_headers.update(response.headers)

        if response.status_code == 200:
            if return_raw:
                return response.text
            # Sometimes, we don't know the content beforehand, so try to decode .json() and
            # if that doesn't work, return the text as is.
            try:
                return response.json()
            except JSONDecodeError:
                return response.text

        # Error handling.
        self._raise_exception(response)

    def _raise_exception(self, response: Response) -> None:
        handlers = {
            400: {
                'invalid request': HttpInvalidRequest
            },
            403: {
                'access blocked': HttpAccessBlocked
            },
            404: {
                '': HttpNotFound
            },
            409: {
                'repository is empty': HttpEmptyRepo
            },
            422: {
                'no commit found': HttpNoCommitFound,
                'invalid state': HttpInvalidState
            },
            429: {
                'too many requests': HttpTooManyRequests,
                'access has been restricted': HttpTooManyRequests
            },
            451: {
                'access blocked': HttpAccessBlocked
            }
        }

        for text, error in handlers.get(response.status_code, {}).items():
            if text in response.text.lower():
                raise error(response)

        raise HttpUnknownError(f"Got a {response.status_code} response with {response.text}")

    def _is_api_rate_limit_error(self, response: Response) -> bool:
        if response.status_code != 403:
            return False
        return 'api rate limit exceeded' in response.text.lower()

    def refresh_tokens(self) -> None:
        self.token_manager.refresh_all()

    def has_valid_token(self) -> bool:
        return self.token_manager.has_valid_token()

    @staticmethod
    def generate_pat_from_gh_app(org: str, private_key: str, client_id: str) -> str | None:
        current_time = int(time.time())
        payload = {
            'iat': current_time - 60,
            'exp': current_time + (1 * 60), # 1 minute lifetime
            'iss': client_id
        }
        encoded_jwt = jwt.encode(payload, private_key, algorithm='RS256')

        headers = {
            'Authorization': f'Bearer {encoded_jwt}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }

        response = requests.get(f"{GitHubApi._api_endpoint}/orgs/{org}/installation", headers=headers)
        if response.status_code != 200:
            return None

        installation_id = response.json()['id']

        response = requests.post(f"{GitHubApi._api_endpoint}/app/installations/{installation_id}/access_tokens", headers=headers)
        if response.status_code == 201:
            return response.json()['token']
        return None
