"""F-008: Nudge Generator.

Produces a single-line session intention based on the latest weekly report
and current dimension levels.  This is the lightweight "session-start nudge" —
one sentence that frames today's work without a lengthy briefing.
"""

from dataclasses import dataclass

from builder_coach.growth_chart import Level
from builder_coach.historical import WeekSnapshot
from builder_coach.report_store import WeeklyReport

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class NudgeContext:
    """Inputs for generating a session nudge."""

    latest_report: WeeklyReport | None
    current_levels: WeekSnapshot | None
    sessions_since_report: int  # sessions since the latest report


# ---------------------------------------------------------------------------
# Internal constants
# ---------------------------------------------------------------------------

# Tie-breaking priority: first entry wins on equal level.
# (Visibility is most commonly neglected, so it leads.)
_PRIORITY_ORDER: list[tuple[str, str]] = [
    ("Visibility", "visibility"),
    ("Leverage Ratio", "leverage_ratio"),
    ("Taste", "taste"),
    ("Ambition Trajectory", "ambition_trajectory"),
    ("Problem Selection", "problem_selection"),
]

# Ordinal rank for level comparison (lower = more room to grow).
_LEVEL_RANK: dict[Level, int] = {
    Level.LOW: 0,
    Level.EMERGING: 1,
    Level.DEVELOPING: 2,
    Level.STRONG: 3,
    Level.EXCEPTIONAL: 4,
}

# Single-sentence nudges for every dimension × level combination.
# Each nudge must:
#   - contain the dimension display name
#   - be < 200 characters
#   - end with exactly one period
#   - have no newlines
#   - avoid "keep going", "push yourself", "stay focused"
_NUDGES: dict[str, dict[Level, str]] = {
    "Visibility": {
        Level.LOW: (
            "Today, take the first step on Visibility: share one artifact "
            "from your current work with a specific person who could benefit from it."
        ),
        Level.EMERGING: (
            "Today, build your Visibility habit by posting one concrete update "
            "— a screenshot, a link, or a lesson — to any public channel."
        ),
        Level.DEVELOPING: (
            "Today, strengthen your Visibility by writing a short post describing "
            "a specific result from your recent sessions and who it helps."
        ),
        Level.STRONG: (
            "Take your Visibility further today by reaching out to a new audience "
            "with your most recent project — a talk pitch, a post, or a direct share."
        ),
        Level.EXCEPTIONAL: (
            "Use your Visibility today to amplify others: introduce two people "
            "in your network who should know each other's work."
        ),
    },
    "Leverage Ratio": {
        Level.LOW: (
            "Before writing a line of code today, spend two minutes on Leverage Ratio: "
            "identify the single change with the largest possible impact."
        ),
        Level.EMERGING: (
            "To build your Leverage Ratio, start this session by listing what to skip "
            "so you can double down on the highest-value work."
        ),
        Level.DEVELOPING: (
            "Today, improve your Leverage Ratio by tracking how many iterations it takes "
            "to reach a satisfying result and consciously aiming for fewer."
        ),
        Level.STRONG: (
            "Challenge your Leverage Ratio today by finding one task you could eliminate "
            "entirely rather than just optimizing it."
        ),
        Level.EXCEPTIONAL: (
            "With your strong Leverage Ratio, today's challenge is teaching one other person "
            "the shortcut you've already mastered."
        ),
    },
    "Taste": {
        Level.LOW: (
            "For today's session, practice Taste by reviewing your last output and writing "
            "one honest sentence about what still isn't working."
        ),
        Level.EMERGING: (
            "Build your Taste today by finding one specific detail in your work that "
            "you would change if you had one more hour."
        ),
        Level.DEVELOPING: (
            "Sharpen your Taste this session by comparing your current work to one example "
            "you genuinely admire and naming the gap between them."
        ),
        Level.STRONG: (
            "Apply your Taste today by removing one element from your current project "
            "that doesn't earn its place in the final result."
        ),
        Level.EXCEPTIONAL: (
            "Use your Taste today to give one specific piece of feedback to someone "
            "whose work you can meaningfully help improve."
        ),
    },
    "Ambition Trajectory": {
        Level.LOW: (
            "To start building your Ambition Trajectory, today's session should tackle "
            "a problem that is slightly larger than anything you have shipped before."
        ),
        Level.EMERGING: (
            "Develop your Ambition Trajectory today by taking on one technical challenge "
            "that sits just beyond your current comfort zone."
        ),
        Level.DEVELOPING: (
            "Today, advance your Ambition Trajectory by scoping a project that requires "
            "you to learn at least one capability you do not yet have."
        ),
        Level.STRONG: (
            "Test the ceiling of your Ambition Trajectory today by proposing a solution "
            "that is an order of magnitude more ambitious than what was asked for."
        ),
        Level.EXCEPTIONAL: (
            "Your Ambition Trajectory is exceptional — today, name the problem you would "
            "work on if you knew that succeeding was guaranteed."
        ),
    },
    "Problem Selection": {
        Level.LOW: (
            "Before starting today, spend five minutes on Problem Selection: write down "
            "why this problem is worth your time over any other."
        ),
        Level.EMERGING: (
            "Today, practice Problem Selection by asking who would be measurably hurt "
            "if this problem stayed unsolved for another year."
        ),
        Level.DEVELOPING: (
            "Sharpen your Problem Selection this session by finding the most important "
            "unsolved sub-problem inside your current project."
        ),
        Level.STRONG: (
            "Today, test your Problem Selection by asking whether there is a harder, "
            "more valuable version of the problem you are already working on."
        ),
        Level.EXCEPTIONAL: (
            "With strong Problem Selection instincts, today's challenge is identifying "
            "the problem that only you are currently positioned to solve."
        ),
    },
}


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------


def select_nudge_dimension(context: NudgeContext) -> str | None:
    """Choose which dimension to nudge on.

    Priority logic:
    1. Lowest-level dimension (most room to grow).
    2. On tie, prefer: Visibility > Leverage Ratio > Taste >
       Ambition Trajectory > Problem Selection.
       (Visibility is most commonly neglected.)
    3. If no level data is available (cold start), return None.

    Args:
        context: NudgeContext with the latest report and current levels.

    Returns:
        Dimension display name (e.g. "Visibility"), or None if no data.
    """
    if context.current_levels is None:
        return None

    # Collect (display_name, level) pairs for dimensions that have data,
    # iterating in priority order so ties resolve to the first found.
    available: list[tuple[str, Level]] = []
    for display_name, field_name in _PRIORITY_ORDER:
        level = getattr(context.current_levels, field_name)
        if level is not None:
            available.append((display_name, level))

    if not available:
        return None

    # Find the minimum rank (lowest level = most room to grow).
    min_rank = min(_LEVEL_RANK[lv] for _, lv in available)

    # Return the first dimension (highest priority) that sits at that rank.
    for display_name, level in available:
        if _LEVEL_RANK[level] == min_rank:
            return display_name

    return None  # unreachable


def format_nudge(
    dimension: str,
    level: Level,
    report_excerpt: str = "",
) -> str:
    """Format a single-line nudge for the selected dimension.

    The nudge is:
    - Exactly one sentence (ends with a single period, no newlines).
    - Specific to the dimension and current level.
    - Actionable for today's session.
    - Not a generic motivational phrase.

    Args:
        dimension: Which dimension to focus on (e.g. "Visibility").
        level: Current level for that dimension.
        report_excerpt: Optional relevant excerpt from the latest report
            (reserved for future use; does not currently alter output).

    Returns:
        A single-line nudge string under 200 characters.
    """
    return _NUDGES[dimension][level]
