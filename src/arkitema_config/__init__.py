import tomllib
from pathlib import Path

pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"

__version__ = tomllib.loads(pyproject.read_text())["tool"]["poetry"]["version"]
