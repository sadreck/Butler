import csv
import os
import json
from requests.models import Response
from src.libs.utils import Utils


class GitHubApiHelper:
    debug_file: str = None

    def _load_debug(self) -> None:
        debug_file = os.getenv('DEBUG_OUTPUT_FILE', '')
        debug_enabled = Utils.is_true(os.getenv('DEBUG_ENABLED', None))
        if debug_enabled and len(debug_file) > 0:
            # Having a value means debug is enabled.
            self.debug_file = debug_file

    def _save_debug(self, url: str, params: dict | None, additional_headers: dict | None, authenticated: bool, response: Response) -> None:
        if self.debug_file is None or len(self.debug_file) == 0:
            return
        # TODO - Make it thread-safe if needed.
        rows = []
        if not os.path.exists(self.debug_file):
            rows.append([
                'request_url',
                'request_params',
                'request_headers',
                'authenticated',
                'response_status',
                'response_headers',
                'response_body',
            ])

        rows.append([
            url,
            json.dumps(params or ''),
            json.dumps(additional_headers or ''),
            authenticated,
            response.status_code,
            json.dumps(dict(response.headers)),
            response.text
        ])
        csv.writer(open(self.debug_file, 'a')).writerows(rows)
