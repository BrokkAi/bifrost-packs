"""Fixed names joined onto the shared temporary directory (BrokkAi/bifrost-packs#443)."""
import os
import os.path
import tempfile
import uuid
from tempfile import gettempdir


def ca_bundle(pem):
    """Reuse a CA bundle at a fixed path, as requests < 2.33.0 did."""
    path = os.path.join(tempfile.gettempdir(), "ca-bundle.pem")
    if not os.path.exists(path):
        with open(path, "w", encoding="ascii") as handle:
            handle.write(pem)
    return path


def lock_path():
    """Return a fixed lock-file path."""
    return os.path.join(gettempdir(), "app.lock")


def cache_path(name):
    """Return a cache path whose name the caller picks."""
    return os.path.join(tempfile.gettempdir(), f"cache-{name}.json")


def random_name():
    """Join a random name onto the temporary directory."""
    return os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)


def random_formatted():
    """Join a name with a random part onto the temporary directory."""
    return os.path.join(tempfile.gettempdir(), f"upload-{uuid.uuid4().hex}.bin")


def random_subdirectory():
    """Put a fixed file name under a random directory."""
    return os.path.join(tempfile.gettempdir(), uuid.uuid4().hex, "data.bin")


def temporary_directory():
    """Return the temporary directory itself."""
    return tempfile.gettempdir()


def secure_file():
    """Create the file exclusively with a random name."""
    handle, path = tempfile.mkstemp(suffix=".pem")
    os.close(handle)
    return path


def private_cache():
    """Join a fixed name onto a directory the application owns."""
    return os.path.join(os.path.expanduser("~/.cache/app"), "ca-bundle.pem")
