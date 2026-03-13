"""Validate recipe YAML files have correct structure and required fields."""

from pathlib import Path

import yaml


BUNDLE_ROOT = Path(__file__).parent.parent
RECIPES_DIR = BUNDLE_ROOT / "recipes"


def _load_recipe(recipe_name: str) -> dict:
    """Load and parse a recipe YAML file."""
    path = RECIPES_DIR / recipe_name
    assert path.is_file(), f"Recipe file not found: {path}"
    return yaml.safe_load(path.read_text())


# --- Weekly Retrospective ---


def test_weekly_retrospective_exists():
    """The weekly retrospective recipe must exist."""
    assert (RECIPES_DIR / "weekly-retrospective.yaml").is_file()


def test_weekly_retrospective_has_required_top_level_fields():
    """Recipe must have name, description, and steps."""
    recipe = _load_recipe("weekly-retrospective.yaml")
    assert recipe.get("name"), "Recipe must have a name"
    assert recipe.get("description"), "Recipe must have a description"
    assert recipe.get("steps"), "Recipe must have steps"
    assert isinstance(recipe["steps"], list), "steps must be a list"


def test_weekly_retrospective_has_four_steps():
    """The weekly retrospective must have exactly 4 steps in the chain."""
    recipe = _load_recipe("weekly-retrospective.yaml")
    steps = recipe["steps"]
    assert len(steps) == 4, (
        f"Expected 4 steps (session-analyst, journal-ingest, coaching, writer), got {len(steps)}"
    )


def test_weekly_retrospective_step_ids():
    """Each step must have an id matching the expected pipeline."""
    recipe = _load_recipe("weekly-retrospective.yaml")
    step_ids = [step["id"] for step in recipe["steps"]]
    expected_ids = ["session-analysis", "journal-ingest", "coaching-evaluation", "write-report"]
    assert step_ids == expected_ids, f"Expected step ids {expected_ids}, got {step_ids}"


def test_weekly_retrospective_steps_have_required_fields():
    """Each step must have id, prompt/instruction, and output."""
    recipe = _load_recipe("weekly-retrospective.yaml")
    for step in recipe["steps"]:
        assert "id" in step, f"Step missing 'id': {step}"
        assert "prompt" in step or "instruction" in step, (
            f"Step '{step.get('id')}' must have 'prompt' or 'instruction'"
        )
        assert "output" in step, f"Step '{step.get('id')}' must have 'output'"


def test_weekly_retrospective_coaching_step_uses_coaching_agent():
    """The coaching evaluation step must delegate to the coaching agent."""
    recipe = _load_recipe("weekly-retrospective.yaml")
    coaching_step = [s for s in recipe["steps"] if s["id"] == "coaching-evaluation"][0]
    assert "agent" in coaching_step, "Coaching step must specify an agent"
    assert "coaching-agent" in coaching_step["agent"], (
        f"Coaching step must use the coaching agent, got: {coaching_step['agent']}"
    )


# --- Session Nudge ---


def test_session_nudge_exists():
    """The session nudge recipe must exist."""
    assert (RECIPES_DIR / "session-nudge.yaml").is_file()


def test_session_nudge_has_required_fields():
    """Session nudge recipe must have name, description, and steps."""
    recipe = _load_recipe("session-nudge.yaml")
    assert recipe.get("name"), "Recipe must have a name"
    assert recipe.get("description"), "Recipe must have a description"
    assert recipe.get("steps"), "Recipe must have steps"


# --- Growth Chart Validation ---


def test_weekly_retrospective_writer_step_includes_chart_format():
    """The writer step must define the text-based growth chart format."""
    recipe = _load_recipe("weekly-retrospective.yaml")
    writer_step = [s for s in recipe["steps"] if s["id"] == "write-report"][0]
    prompt = writer_step.get("prompt", "")
    assert "YOUR BUILDER SHAPE" in prompt, (
        "Writer step must include the text-based radar chart template"
    )


def test_weekly_retrospective_writer_step_references_all_dimensions():
    """The writer step chart must reference all five dimensions."""
    recipe = _load_recipe("weekly-retrospective.yaml")
    writer_step = [s for s in recipe["steps"] if s["id"] == "write-report"][0]
    prompt = writer_step.get("prompt", "")
    dimensions = ["Problem Selection", "Leverage Ratio", "Taste", "Ambition", "Visibility"]
    for dim in dimensions:
        assert dim in prompt, f"Writer step chart must reference '{dim}'"


def test_weekly_retrospective_writer_saves_to_reports_dir():
    """The writer step must save the report to the reports directory."""
    recipe = _load_recipe("weekly-retrospective.yaml")
    writer_step = [s for s in recipe["steps"] if s["id"] == "write-report"][0]
    prompt = writer_step.get("prompt", "")
    assert "reports_dir" in prompt or "reports/" in prompt, (
        "Writer step must save report to the reports directory"
    )
