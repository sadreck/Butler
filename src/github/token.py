import requests
import json
from datetime import datetime


class TokenInstance:
    _access_token: str = None
    _valid: bool = None
    _usage: int = None
    _rate_limit: tuple[int, datetime] = None
    _refresh_token_every: int = 10

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def access_token_masked(self) -> str:
        size = 8 if self.access_token.startswith('ghp_') else 16
        return f"{self.access_token[:size]}****"

    @property
    def valid(self) -> bool:
        return self._valid or False

    @property
    def remaining_calls(self) -> int:
        return 0 if self._rate_limit is None else self._rate_limit[0]

    @property
    def resets_at(self) -> datetime | str:
        return 'NoDateFound' if self._rate_limit is None else self._rate_limit[1]

    @property
    def usage(self) -> int:
        return self._usage

    def __init__(self, access_token: str):
        self._access_token = access_token
        self._usage = 0

    def _get_rate_limit(self) -> tuple[int, datetime]:
        response = requests.get(
            'https://api.github.com/rate_limit',
            headers={
                'Authorization': f"token {self.access_token}",
                'Accept': 'application/vnd.github.v3+json'
            }
        )
        # This function is only called from .refresh(), if there's an exception the token is marked as invalid.
        response.raise_for_status()
        data = json.loads(response.text)
        core = data.get('resources', {}).get('core', {})
        return core.get('remaining', 0), datetime.fromtimestamp(core.get('reset', 0))

    def refresh(self) -> None:
        try:
            self._rate_limit = self._get_rate_limit()
            self._valid = self.remaining_calls > 0
        except Exception as e:
            self._valid = False

    def increase_usage(self) -> int:
        self._usage += 1
        if self._usage % self._refresh_token_every == 0:
            self.refresh()
        return self._usage
