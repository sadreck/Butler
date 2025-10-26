import os
import sys
import csv
import hashlib
from src.libs.utils import Utils


def convert(http_log: str, asset_parent_folder: str, asset_path: str) -> str:
    lines = []
    with open(http_log, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = hashlib.md5(row['request_url'].encode()).hexdigest()
            headers_file = f"{asset_parent_folder}/{filename}.headers.json"
            contents_file = f"{asset_parent_folder}/{filename}.contents.json"

            if not Utils.write_file(os.path.join(asset_path, headers_file), row['response_headers']):
                print(f"Could not write {os.path.join(asset_path, headers_file)}")
                exit(1)
            if not Utils.write_file(os.path.join(asset_path, contents_file), row['response_body']):
                print(f"Could not write {os.path.join(asset_path, contents_file)}")
                exit(1)

            is_json = 'True' if (row['response_body'].startswith('{') or row['response_body'].startswith('[')) else 'False'

            line = f"'{row['request_url']}': MockResponse('{contents_file}', '{headers_file}', {row['response_status']}, is_json_contents={is_json})"

            lines.append(line)

    return ",\n".join(lines)

if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else None
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    if input_file is None:
        print("No input file set")
        exit(1)
    elif output_path is None:
        print("No output path set")
        exit(1)
    output = convert(input_file, 'vscode-download', output_path)
    print(output)
