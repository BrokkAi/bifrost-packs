import sys
import venv

from build_paths import resolve_env_dir


def create_through_helper():
    venv.create(resolve_env_dir(sys.argv[1]))
