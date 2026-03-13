"""Validate the coaching agent has correct frontmatter and structure."""

from pathlib import Path

import yaml


BUNDLE_ROOT = Path(__file__).parent.parent
AGENT_PATH = BUNDLE_ROOT / "agents" / "coaching-agent.md"


def _parse_agent_frontmatter(agent_path: Path) -> dict:
    """Extract YAML frontmatter from an agent markdown file."""
    text = agent_path.read_text()
    assert text.startswith("---"), f"{agent_path} must start with YAML frontmatter (---)"
    parts = text.split("---", 2)
    assert len(parts) >= 3, f"{agent_path} must have opening and closing --- for frontmatter"
    return yaml.safe_load(parts[1])


def test_coaching_agent_file_exists():
    """The coaching agent file must exist."""
    assert AGENT_PATH.is_file(), f"agents/coaching-agent.md not found at {AGENT_PATH}"


def test_coaching_agent_has_meta_name():
    """The agent must declare meta.name in frontmatter."""
    fm = _parse_agent_frontmatter(AGENT_PATH)
    meta = fm.get("meta", {})
    assert meta.get("name") == "coaching-agent", (
        f"Expected meta.name 'coaching-agent', got {meta.get('name')}"
    )


def test_coaching_agent_has_description():
    """The agent must have a description in meta."""
    fm = _parse_agent_frontmatter(AGENT_PATH)
    meta = fm.get("meta", {})
    assert meta.get("description"), "meta.description is required"
    assert len(meta["description"]) > 50, "meta.description should be substantive"


def test_coaching_agent_references_growth_framework():
    """The agent body must reference the growth framework context file."""
    text = AGENT_PATH.read_text()
    assert "growth-framework.md" in text, (
        "Agent must reference @builder-coach:context/growth-framework.md"
    )


def test_coaching_agent_defines_output_format():
    """The agent must specify an output format section."""
    text = AGENT_PATH.read_text()
    assert "Output Format" in text or "output format" in text.lower(), (
        "Agent must define an output format for downstream agents to consume"
    )


def test_coaching_agent_lists_all_five_dimensions():
    """The agent instructions must reference all five growth dimensions."""
    text = AGENT_PATH.read_text()
    dimensions = [
        "Problem Selection",
        "Leverage Ratio",
        "Taste",
        "Ambition Trajectory",
        "Visibility",
    ]
    for dim in dimensions:
        assert dim in text, f"Agent must reference dimension '{dim}'"


def test_coaching_agent_handles_cold_start():
    """The agent must have instructions for first-week bootstrap."""
    text = AGENT_PATH.read_text().lower()
    assert "cold start" in text or "first week" in text or "no history" in text, (
        "Agent must include cold start / first week handling instructions"
    )


def test_coaching_agent_supports_session_only_evaluation():
    """Agent must describe session-only evaluation path."""
    lower = AGENT_PATH.read_text().lower()
    assert "session data" in lower or "session history" in lower, (
        "Agent must describe session-only evaluation capability"
    )


def test_coaching_agent_visibility_not_journal_only():
    """Visibility must be evaluable from session data, not journal-only."""
    lines = AGENT_PATH.read_text().split("\n")
    in_vis = False
    vis_lines = []
    for line in lines:
        if line.strip().startswith("### Visibility"):
            in_vis = True
            continue
        elif in_vis and line.strip().startswith("### "):
            break
        elif in_vis:
            vis_lines.append(line)
    vis_section = "\n".join(vis_lines).lower()
    assert "primarily from journal" not in vis_section, (
        "Visibility section must not say 'primarily from journal' — "
        "it should describe session-data signals"
    )


def test_coaching_agent_on_demand_framing():
    """Output format must not be hardcoded to weekly framing."""
    text = AGENT_PATH.read_text()
    assert "Week of [DATE]" not in text, (
        "Output format should use scope-aware framing, not 'Week of [DATE]'"
    )


def test_coaching_agent_signal_transparency():
    """Agent must describe signal strength / confidence calibration."""
    lower = AGENT_PATH.read_text().lower()
    assert "signal" in lower or "confidence" in lower or "calibrat" in lower, (
        "Agent must describe how to calibrate evaluation to available signal"
    )
