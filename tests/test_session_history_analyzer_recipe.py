"""Tests for the session-history-analyzer recipe structure."""

from pathlib import Path

import yaml

_RECIPE_PATH = Path(__file__).parent.parent / "recipes" / "session-history-analyzer.yaml"


def test_recipe_file_exists():
    assert _RECIPE_PATH.exists(), "recipes/session-history-analyzer.yaml must exist"


def test_recipe_has_valid_yaml():
    content = _RECIPE_PATH.read_text()
    recipe = yaml.safe_load(content)
    assert isinstance(recipe, dict)


def test_recipe_has_name():
    recipe = yaml.safe_load(_RECIPE_PATH.read_text())
    assert recipe.get("name") == "session-history-analyzer"


def test_recipe_has_steps():
    recipe = yaml.safe_load(_RECIPE_PATH.read_text())
    steps = recipe.get("steps", [])
    assert len(steps) >= 2, "Recipe needs at least 2 steps (evidence + coaching)"


def test_recipe_step_ids():
    recipe = yaml.safe_load(_RECIPE_PATH.read_text())
    step_ids = [s["id"] for s in recipe["steps"]]
    assert "gather-evidence" in step_ids
    assert "coaching-evaluation" in step_ids


def test_recipe_uses_coaching_agent():
    recipe = yaml.safe_load(_RECIPE_PATH.read_text())
    steps = recipe.get("steps", [])
    agents = [s.get("agent", "") for s in steps]
    assert any("coaching-agent" in a for a in agents)


def test_recipe_has_reports_dir_context():
    recipe = yaml.safe_load(_RECIPE_PATH.read_text())
    context = recipe.get("context", {})
    assert "reports_dir" in context, "Recipe needs reports_dir for report storage"
