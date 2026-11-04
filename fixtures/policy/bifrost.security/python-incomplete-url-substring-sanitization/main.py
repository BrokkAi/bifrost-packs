from helpers import unsafe_prefix, unsafe_suffix, safe_suffix, unsafe_substring


def route(url):
    return unsafe_prefix(url), unsafe_suffix(url), safe_suffix(url), unsafe_substring(url)
