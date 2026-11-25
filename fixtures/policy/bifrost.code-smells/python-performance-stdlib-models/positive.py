import json
import pickle
import re


def decode_events(lines):
    events = []
    for line in lines:
        events.append(json.loads(line))
        events.append(json.loads(line, parse_float=float))
        events.append(json.dumps(line, indent=2, sort_keys=True))
        events.append(re.compile(line))
        events.append(re.compile(line, re.IGNORECASE))
        events.append(pickle.loads(line, encoding="latin1"))
        events.append(pickle.dumps(line, 4))
    return events
