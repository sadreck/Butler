from loguru import logger
from src.github.exceptions import NoValidAccessToken, ApiRateLimitExceeded
from src.github.token import TokenInstance


class TokenManager:
    _tokens: list[TokenInstance] = None
    log: logger = None
    _is_loaded: bool = None

    def __init__(self, access_tokens: list[str], log: logger):
        self.log = log
        self._tokens = [TokenInstance(access_tokens) for access_tokens in access_tokens]
        self._is_loaded = False

    def _load(self) -> None:
        has_valid = False
        for instance in self._tokens:
            instance.refresh()
            if instance.valid:
                has_valid = True
                self.log.info(f"Remaining calls for {instance.access_token_masked}:{instance.remaining_calls}")
                continue

            if instance.remaining_calls == 0 and instance.resets_at != 'NoDateFound':
                self.log.error(f"API Limit reached for access token: {instance.access_token_masked}. Token resets at {instance.resets_at}")
            else:
                self.log.error(f"Invalid access token: {instance.access_token_masked}")
        if not has_valid:
            raise NoValidAccessToken("No valid access token passed")

    def has_valid_token(self) -> bool:
        return any(instance.valid for instance in self._tokens)

    def refresh_all(self) -> None:
        for instance in self._tokens:
            instance.refresh()

    def instance(self) -> TokenInstance:
        """
        If there is only one instance:
            1. Check if it's valid.
            2. If it isn't, refresh.
            3. If it still isn't valid, throw exception.
            4. If it is valid, return.

        If there are more than one instances:
            1. Find the first valid instance that is _after_ the current instance index (to ensure rolling usage).
            2. Return that instance.
            3. If there are no other valid instances, refresh them all.
            4. If there are still no valid instances, throw exception.
            5. Otherwise, return the first valid one.
        """
        if not self._is_loaded:
            self._load()
            self._is_loaded = True

        if len(self._tokens) == 1:
            if not self._tokens[0].valid:
                self._tokens[0].refresh()
                if not self._tokens[0].valid:
                    self._show_instance_reset_times()
                    raise ApiRateLimitExceeded("All tokens have exceeded their API limits")
            self._tokens[0].increase_usage()
            return self._tokens[0]

        next_instance_index = self._find_next_instance()
        if next_instance_index is None:
            self.refresh_all()
            next_instance_index = self._find_next_instance()
            if next_instance_index is None:
                self._show_instance_reset_times()
                raise ApiRateLimitExceeded("All tokens have exceeded their API limits")

        self._tokens[next_instance_index].increase_usage()
        return self._tokens[next_instance_index]

    def _show_instance_reset_times(self) -> None:
        for instance in self._tokens:
            instance.refresh()
            self.log.info(f"API token {instance.access_token_masked} resets at {instance.resets_at}")

    def _find_next_instance(self) -> int | None:
        return next((index for index, instance in enumerate(self._tokens) if instance.valid), None)
