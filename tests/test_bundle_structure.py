"""Validate the bundle.md manifest has correct YAML frontmatter and structure."""

from pathlib import Path

import yaml


BUNDLE_ROOT = Path(__file__).parent.parent


def _parse_bundle_frontmatter(bundle_path: Path) -> dict:
    """Extract YAML frontmatter from a markdown file with --- delimiters."""
    text = bundle_path.read_text()
    assert text.startswith("---"), f"{bundle_path} must start with YAML frontmatter (---)"
    # Split on '---' — first element is empty, second is YAML, rest is markdown body
    parts = text.split("---", 2)
    assert len(parts) >= 3, f"{bundle_path} must have opening and closing --- for frontmatter"
    return yaml.safe_load(parts[1])


def test_bundle_md_exists():
    """bundle.md must exist at the project root."""
    assert (BUNDLE_ROOT / "bundle.md").is_file(), "bundle.md not found at project root"


def test_bundle_frontmatter_parses():
    """bundle.md frontmatter must be valid YAML."""
    fm = _parse_bundle_frontmatter(BUNDLE_ROOT / "bundle.md")
    assert fm is not None, "Frontmatter parsed to None"
    assert isinstance(fm, dict), f"Frontmatter must be a dict, got {type(fm)}"


def test_bundle_has_required_fields():
    """bundle.md must declare name, version, and description."""
    fm = _parse_bundle_frontmatter(BUNDLE_ROOT / "bundle.md")
    bundle = fm.get("bundle", {})
    assert bundle.get("name") == "builder-coach", (
        f"Expected name 'builder-coach', got {bundle.get('name')}"
    )
    assert bundle.get("version"), "bundle.version is required"
    assert bundle.get("description"), "bundle.description is required"


def test_bundle_includes_foundation():
    """bundle.md must include the foundation bundle."""
    fm = _parse_bundle_frontmatter(BUNDLE_ROOT / "bundle.md")
    includes = fm.get("includes", [])
    bundle_refs = [inc.get("bundle", "") for inc in includes if isinstance(inc, dict)]
    foundation_found = any("foundation" in ref for ref in bundle_refs)
    assert foundation_found, f"Must include foundation bundle. Found includes: {bundle_refs}"


def test_required_directories_exist():
    """All required directories must exist."""
    required_dirs = ["recipes", "agents", "context", "data", "data/reports", "tests"]
    for dirname in required_dirs:
        assert (BUNDLE_ROOT / dirname).is_dir(), f"Required directory '{dirname}/' is missing"


def test_agents_declared_in_bundle():
    """bundle.md must declare the coaching-agent."""
    fm = _parse_bundle_frontmatter(BUNDLE_ROOT / "bundle.md")
    agents = fm.get("agents", {})
    includes = agents.get("include", [])
    assert any("coaching-agent" in ref for ref in includes), (
        f"coaching-agent must be declared in bundle.md agents.include. Found: {includes}"
    )


def test_bundle_includes_recipes_bundle():
    """The bundle must include amplifier-bundle-recipes for recipe execution."""
    fm = _parse_bundle_frontmatter(BUNDLE_ROOT / "bundle.md")
    includes = fm.get("includes", [])
    sources = [inc.get("bundle", "") for inc in includes if isinstance(inc, dict)]
    assert any("amplifier-bundle-recipes" in s for s in sources), (
        "bundle.md must include amplifier-bundle-recipes in includes"
    )


def test_growth_framework_not_in_context_include():
    """Growth framework should be loaded via @mention only, not context.include."""
    fm = _parse_bundle_frontmatter(BUNDLE_ROOT / "bundle.md")
    context = fm.get("context", {})
    includes = context.get("include", []) if context else []
    framework_refs = [i for i in includes if "growth-framework" in str(i)]
    assert len(framework_refs) == 0, (
        "growth-framework.md should not be in context.include — "
        "it is already @mentioned in coaching-agent.md"
    )


def test_coach_instructions_file_exists():
    """Coach instructions context file must exist for recipe dispatch."""
    path = Path(__file__).parent.parent / "context" / "coach-instructions.md"
    assert path.exists(), "context/coach-instructions.md is required"


def test_coach_instructions_references_recipes():
    """Coach instructions must reference all available recipes."""
    path = Path(__file__).parent.parent / "context" / "coach-instructions.md"
    content = path.read_text()
    assert "session-history-analyzer" in content
    assert "session-nudge" in content
    assert "weekly-retrospective" in content


def _bundle_body(bundle_path: Path) -> str:
    """Return the markdown body (everything after frontmatter) from bundle.md."""
    text = bundle_path.read_text()
    parts = text.split("---", 2)
    assert len(parts) >= 3, "bundle.md must have valid frontmatter"
    return parts[2]


def test_automated_workflows_lists_three_recipes():
    """Automated Workflows section must declare 3 Recipes (session-history-analyzer added)."""
    body = _bundle_body(BUNDLE_ROOT / "bundle.md")
    assert "3 Recipes" in body, (
        "Automated Workflows heading must say '3 Recipes' — session-history-analyzer was added"
    )


def test_session_history_analyzer_listed_in_workflows():
    """session-history-analyzer must appear in the Automated Workflows section."""
    body = _bundle_body(BUNDLE_ROOT / "bundle.md")
    assert "session-history-analyzer" in body, (
        "session-history-analyzer must be listed as an automated workflow in bundle.md"
    )


def test_quick_start_leads_with_analyze_sessions():
    """Quick Start must lead with the session history analyzer command."""
    body = _bundle_body(BUNDLE_ROOT / "bundle.md")
    assert "Analyze my sessions" in body, (
        "Quick Start must include 'Analyze my sessions' as the primary command"
    )
