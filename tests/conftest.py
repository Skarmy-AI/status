import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def upptimerc():
    return yaml.safe_load((REPO_ROOT / ".upptimerc.yml").read_text())


@pytest.fixture(scope="session")
def history_summary():
    return json.loads((REPO_ROOT / "history" / "summary.json").read_text())
