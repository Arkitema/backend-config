from pathlib import Path

import tomllib

from arkitema_config import __version__


def test_version():
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    assert __version__ == tomllib.loads(pyproject.read_text())["tool"]["poetry"]["version"]
