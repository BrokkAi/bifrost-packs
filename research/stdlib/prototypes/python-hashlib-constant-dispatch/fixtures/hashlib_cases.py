import hashlib as hashes
from hashlib import new as new_hash
from hashlib import sha256 as imported_sha256


def module_alias(data):
    return hashes.new("sha256", data)


def module_alias_with_flag(data):
    return hashes.new("sha256", data, usedforsecurity=False)


def from_import_alias(data):
    return new_hash('sha256', data)


def from_import_alias_keywords(data):
    return new_hash(name="sha256", data=data, usedforsecurity=False)


def from_import_alias_omitted_data():
    return new_hash("sha256")


def keyword_name_and_data(data):
    return hashes.new(name="sha256", data=data, usedforsecurity=False)


def dynamic_name(name, data):
    return hashes.new(name, data)


def direct_named_constructor(data):
    return hashes.sha256(data)


def imported_named_constructor(data):
    return imported_sha256(data)


def omitted_data():
    return hashes.new("sha256")


def keyword_name_without_data():
    return hashes.new(name="sha256", usedforsecurity=False)


def extra_positional_argument(data):
    # The call shape is invalid for hashlib.new; exact positional arity
    # prevents it from entering the candidate query.
    return hashes.new("sha256", data, False)


def shake_is_a_named_constructor(data):
    return hashes.new("shake_128", data)


def md5_is_fips_sensitive(data):
    return hashes.new("md5", data, usedforsecurity=False)


def provider_specific_name(data):
    return hashes.new("ripemd160", data)


def shadowed_module_parameter(hashlib, data):
    return hashlib.new("sha256", data)


def shadowed_module_local(data):
    hashlib = LocalHashlib()
    return hashlib.new("sha256", data)


class LocalHashlib:
    def new(self, algorithm, data):
        return algorithm, data
