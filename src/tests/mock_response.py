import os
import json
from src.libs.utils import Utils
from unittest.mock import Mock


class MockResponse:
    contents: str | None = None
    headers: dict | None = None
    status_code: int | None = None
    is_json_contents: bool = None

    def __init__(self, contents_file: str | None, headers_file: str | None, status_code: int, is_json_contents: bool = True):
        self.contents = ''
        self.headers = {}
        self.is_json_contents = is_json_contents

        self.contents = self._read_file(contents_file, False)
        self.headers = self._read_file(headers_file, True) or {}
        self.status_code = status_code

    def _read_file(self, path: str | None, is_json: bool) -> str | None | dict | list:
        assets_path = Utils.get_tests_assets_folder().rstrip('/')

        if path is None:
            return None
        path = os.path.join(assets_path, path.lstrip('/'))
        if not os.path.exists(path):
            raise Exception(f"{path} does not exist")
        contents = Utils.read_file(path)
        return json.loads(contents) if is_json else contents

    def response(self) -> Mock:
        mock_response = Mock()
        mock_response.status_code = self.status_code
        if self.is_json_contents:
            mock_response.json.return_value = json.loads(self.contents)
        else:
            mock_response.json.side_effect = json.JSONDecodeError("Expecting value", self.contents, 0)
        mock_response.text = self.contents
        mock_response.headers = self.headers
        return mock_response
