import hashlib
import json
import platform
import sys


ALGORITHMS = (
    "sha1",
    "sha224",
    "sha256",
    "sha384",
    "sha512",
    "sha3_224",
    "sha3_256",
    "sha3_384",
    "sha3_512",
    "shake_128",
    "shake_256",
    "blake2b",
    "blake2s",
)
PAYLOAD = b"hashlib constant-dispatch probe"


def digest(value, algorithm):
    if algorithm.startswith("shake_"):
        return value.hexdigest(32)
    return value.hexdigest()


assert sys.version_info >= (3, 9), "witness requires usedforsecurity support"
results = []
for algorithm in ALGORITHMS:
    named = getattr(hashlib, algorithm, None)
    assert callable(named), f"missing local named constructor: {algorithm}"
    via_new = hashlib.new(algorithm, PAYLOAD, usedforsecurity=False)
    via_named = named(PAYLOAD, usedforsecurity=False)
    assert digest(via_new, algorithm) == digest(via_named, algorithm), algorithm
    empty_via_new = hashlib.new(algorithm, usedforsecurity=False)
    empty_via_named = named(usedforsecurity=False)
    assert digest(empty_via_new, algorithm) == digest(empty_via_named, algorithm), algorithm
    results.append(algorithm)

via_new_keywords = hashlib.new(
    name="sha256", data=PAYLOAD, usedforsecurity=False
)
via_named_positional = hashlib.sha256(PAYLOAD, usedforsecurity=False)
assert via_new_keywords.digest() == via_named_positional.digest()

empty_via_new = hashlib.new("sha256")
empty_via_named = hashlib.sha256()
assert empty_via_new.digest() == empty_via_named.digest()

try:
    hashlib.sha256(data=PAYLOAD)
except TypeError:
    named_data_keyword_rejected = True
else:
    raise AssertionError("sha256(data=...) unexpectedly accepted on this runtime")

try:
    hashlib.new("__not_a_hashlib_algorithm__", PAYLOAD)
except ValueError:
    unknown_name_rejected = True
else:
    raise AssertionError("unknown algorithm unexpectedly accepted")

print(
    json.dumps(
        {
            "status": "supported_on_recorded_runtime",
            "runtime": platform.python_implementation()
            + " "
            + platform.python_version(),
            "platform": platform.platform(),
            "hashlib_file_basename": "hashlib.py",
            "compared_algorithms": list(results),
            "usedforsecurity_false_preserved": True,
            "new_name_and_data_keywords_supported": True,
            "named_constructor_data_keyword_rejected": named_data_keyword_rejected,
            "omitted_new_data_equals_named_constructor_default": True,
            "unknown_algorithm_rejected": unknown_name_rejected,
            "target_runtime_claim": False,
            "performance_measured": False,
        },
        sort_keys=True,
    )
)
