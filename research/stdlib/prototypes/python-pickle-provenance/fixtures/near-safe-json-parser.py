import json
import os


def parse_json_record():
    document = os.environ["JSON_DOCUMENT"]
    return json.loads(document)
