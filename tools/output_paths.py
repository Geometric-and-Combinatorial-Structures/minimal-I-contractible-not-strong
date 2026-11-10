"""Keep generated files out of distributed inputs."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def generated_output(path):
    path = Path(path).resolve()
    if path.is_relative_to(ROOT):
        parts = path.relative_to(ROOT).parts
        if len(parts) < 2 or parts[0] not in ("results", "build"):
            raise ValueError("Inside the repository, choose a subdirectory of root results/ or build/")
    return path
