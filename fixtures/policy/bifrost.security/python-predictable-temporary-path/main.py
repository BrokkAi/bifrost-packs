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


def pid_file():
    """Return a fixed pid-file path."""
    return os.path.join(tempfile.gettempdir(), "worker.pid")


def random_name():
    """Join a random name onto the temporary directory."""
    return os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)


def random_formatted():
    """Join a name with a random part onto the temporary directory."""
    return os.path.join(tempfile.gettempdir(), f"upload-{uuid.uuid4().hex}.bin")


def random_token():
    """Interpolate a random token held in a local."""
    token = uuid.uuid4().hex
    return os.path.join(tempfile.gettempdir(), f"upload-{token}.bin")


def caller_name(name):
    """Interpolate a name the caller picks (not examined)."""
    return os.path.join(tempfile.gettempdir(), f"cache-{name}.json")


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


class Segments:
    """A local helper whose join method builds no filesystem path."""

    def join(self, *parts):
        """Join the parts with a separator."""
        return ":".join(parts)


def unrelated_join():
    """Pass the temporary directory to an unrelated join method."""
    return Segments().join(tempfile.gettempdir(), "cache")


class Route:
    """A local object whose path attribute has its own join method."""

    def __init__(self):
        """Use a Segments helper as the path attribute."""
        self.path = Segments()


def attribute_join():
    """Pass the temporary directory to a join method on an attribute named path."""
    return Route().path.join(tempfile.gettempdir(), "cache")
