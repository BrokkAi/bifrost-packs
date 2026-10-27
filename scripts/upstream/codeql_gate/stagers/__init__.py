"""Language staging protocol shared by upstream-test gates."""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PreparedRoot:
    root: Path
    source_paths: tuple[str, ...]
    staged_artifacts: tuple[dict, ...] = ()
