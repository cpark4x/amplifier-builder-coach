"""Validate the growth framework context file is complete and well-structured."""

from pathlib import Path


BUNDLE_ROOT = Path(__file__).parent.parent
FRAMEWORK_PATH = BUNDLE_ROOT / "context" / "growth-framework.md"

REQUIRED_DIMENSIONS = [
    "Problem Selection",
    "Leverage Ratio",
    "Taste",
    "Ambition Trajectory",
    "Visibility",
]

REQUIRED_LEVELS = [
    "Low",
    "Emerging",
    "Developing",
    "Strong",
    "Exceptional",
]


def test_growth_framework_file_exists():
    """The growth framework context file must exist."""
    assert FRAMEWORK_PATH.is_file(), f"context/growth-framework.md not found at {FRAMEWORK_PATH}"


def test_all_five_dimensions_present():
    """The framework must define all five growth dimensions."""
    text = FRAMEWORK_PATH.read_text()
    for dimension in REQUIRED_DIMENSIONS:
        assert dimension in text, f"Dimension '{dimension}' not found in growth-framework.md"


def test_all_qualitative_levels_defined_per_dimension():
    """Each dimension must have all five qualitative levels defined."""
    text = FRAMEWORK_PATH.read_text()

    # Split by dimension headers (## headings that contain dimension names)
    for dimension in REQUIRED_DIMENSIONS:
        # Find the section for this dimension
        dim_start = text.find(dimension)
        assert dim_start != -1, f"Dimension '{dimension}' not found"

        # Get text from this dimension to the next ## heading or end of file
        remaining = text[dim_start:]
        next_section = remaining.find("\n## ", 1)
        if next_section != -1:
            section_text = remaining[:next_section]
        else:
            section_text = remaining

        for level in REQUIRED_LEVELS:
            assert level in section_text, (
                f"Level '{level}' not found in dimension '{dimension}' section"
            )


def test_impact_moments_section_present():
    """The framework must include an Impact Moments section."""
    text = FRAMEWORK_PATH.read_text()
    assert "Impact Moments" in text, "Impact Moments section not found in growth-framework.md"


def test_framework_explains_what_each_dimension_measures():
    """Each dimension section should explain what it measures."""
    text = FRAMEWORK_PATH.read_text()
    # Each dimension should have a "What it measures" or descriptive paragraph
    for dimension in REQUIRED_DIMENSIONS:
        dim_start = text.find(dimension)
        remaining = text[dim_start:]
        next_section = remaining.find("\n## ", 1)
        section_text = remaining[:next_section] if next_section != -1 else remaining
        # Each dimension section should be substantial (at least 200 chars with levels)
        assert len(section_text) > 200, (
            f"Dimension '{dimension}' section seems too short ({len(section_text)} chars). "
            "Should include description + all 5 qualitative levels."
        )


def test_framework_distinguishes_visibility_from_impact():
    """The framework must explain the Visibility vs Impact Moments distinction."""
    text = FRAMEWORK_PATH.read_text()
    # Look for the distinction being made explicit
    assert "leading indicator" in text.lower() or "lagging indicator" in text.lower(), (
        "Framework should explain that Visibility is a leading indicator and "
        "Impact Moments is a lagging indicator"
    )
