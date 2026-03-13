# Builder's Mirror Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Build an Amplifier bundle that acts as a metacognitive coach for AI builders — analyzing session logs + self-reported events against a growth framework, producing weekly coaching letters and session-start nudges.

**Architecture:** An Amplifier bundle (`amplifier-builders-mirror`) containing a coaching agent (markdown), two recipes (YAML), a growth framework context file (markdown), and a growth journal (markdown). The core product is a weekly retrospective recipe that chains four agents: session-analyst → journal-ingest → coaching-agent → writer-agent. A lightweight session-nudge recipe produces a single-line intention at session start.

**Tech Stack:** Amplifier bundle (YAML recipes + markdown agents), Python (pytest for structural validation tests), no external dependencies.

**Design Document:** `docs/plans/2026-03-11-builders-mirror-design.md`

---

## Scope

**V1 (this plan):**
- Weekly retrospective recipe (4-step chain)
- Session-start nudge recipe
- Coaching agent with growth framework evaluation logic
- Growth framework context file (5 dimensions × 5 qualitative levels + Impact Moments)
- Growth journal template (free-form markdown with date headers)
- Text-based growth chart in weekly report
- One-file-per-week report storage

**Deferred (NOT in this plan):**
- Live nudging (real-time session warnings)
- External API integrations (GitHub, Substack)
- Image-based charts
- Multi-user support

---

## Bundle Structure

```
amplifier-builders-mirror/
├── bundle.md                          # Root bundle manifest
├── pyproject.toml                     # Toolchain config (pytest, ruff)
├── recipes/
│   ├── weekly-retrospective.yaml      # Core product — 4-step coaching pipeline
│   └── session-nudge.yaml             # Single-line session intention
├── agents/
│   └── coaching-agent.md              # Evaluates sessions against growth framework
├── context/
│   └── growth-framework.md            # 5 dimensions + qualitative levels + Impact Moments
├── data/
│   ├── growth-journal.md              # Self-reported events (user edits this)
│   └── reports/                       # Weekly report files (one per week)
│       └── .gitkeep                   # Keeps empty dir in git
├── tests/
│   ├── test_bundle_structure.py       # Bundle manifest validation
│   ├── test_recipe_schema.py          # Recipe YAML validation
│   ├── test_coaching_agent.py         # Agent frontmatter validation
│   └── test_growth_framework.py       # Framework completeness checks
└── docs/
    └── plans/                         # Design + implementation plans
        ├── 2026-03-11-builders-mirror-design.md
        └── 2026-03-11-builders-mirror-implementation.md
```

---

## Task Dependencies

```
Task 1 (Scaffold) ──► Task 2 (Growth Framework) ──► Task 3 (Coaching Agent)
                                                          │
                                                          ▼
                                                    Task 4 (Weekly Retrospective Recipe)
                                                          │
                                                          ▼
                                                    Task 5 (Session-Start Nudge Recipe)

Task 1 (Scaffold) ──► Task 6 (Growth Journal + Report Storage)

Task 4 (Weekly Retro) ──► Task 7 (Growth Chart in Writer Step)
```

Tasks 2 and 6 can run in parallel after Task 1.
Task 3 depends on Task 2.
Task 4 depends on Task 3.
Task 5 depends on Task 4.
Task 7 depends on Task 4.

---

## Task 1: Scaffold

Create the project repo, directory structure, bundle manifest, and toolchain config.

**Files:**
- Create: `amplifier-builders-mirror/bundle.md`
- Create: `amplifier-builders-mirror/pyproject.toml`
- Create: `amplifier-builders-mirror/.gitignore`
- Create: `amplifier-builders-mirror/data/reports/.gitkeep`
- Create: `amplifier-builders-mirror/tests/test_bundle_structure.py`

### Step 1: Create the project directory

Run:
```bash
cd /Users/chrispark/Projects
mkdir -p amplifier-builders-mirror/{recipes,agents,context,data/reports,tests,docs/plans}
```

### Step 2: Initialize git

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
git init
```
Expected: `Initialized empty Git repository in /Users/chrispark/Projects/amplifier-builders-mirror/.git/`

### Step 3: Create .gitignore

Create `amplifier-builders-mirror/.gitignore`:
```
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
build/
.venv/
.ruff_cache/
```

### Step 4: Create pyproject.toml

Create `amplifier-builders-mirror/pyproject.toml`:
```toml
[project]
name = "amplifier-builders-mirror"
version = "0.1.0"
description = "Metacognitive coaching bundle for AI builders"
requires-python = ">=3.11"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pyyaml>=6.0",
    "ruff>=0.4",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
target-version = "py311"
line-length = 100
```

### Step 5: Create the .gitkeep for reports directory

Create `amplifier-builders-mirror/data/reports/.gitkeep` as an empty file. Its only purpose is to keep the `data/reports/` directory in git.

### Step 6: Create bundle.md

This is the root manifest. It tells Amplifier what this bundle provides. Pattern is based on existing bundles like `amplifier-bundle-stories/bundle.md` and `amplifier-bundle-ui-vision/bundle.md`.

Create `amplifier-builders-mirror/bundle.md`:
```markdown
---
bundle:
  name: builders-mirror
  version: 0.1.0
  description: >
    Metacognitive coaching for AI builders. Analyzes Amplifier session history
    and self-reported events against a growth framework to produce weekly
    coaching letters and session-start nudges.

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main

agents:
  include:
    - builders-mirror:coaching-agent

context:
  include:
    - builders-mirror:context/growth-framework.md
---

# Builder's Mirror

**Metacognitive coaching for AI builders.**

Coding is solved. What matters now is problem selection, leverage, taste, ambition, and visibility. But you can't improve what you can't see. Builder's Mirror analyzes how you work with AI and reflects your growth back to you — a mirror that shows your shape as a builder and how that shape is changing over time.

## What This Bundle Provides

### Growth Framework
Five dimensions that define what makes someone an invaluable AI builder:
- **Problem Selection** — Are you choosing to work on things that matter?
- **Leverage Ratio** — How much output per unit of input?
- **Taste** — Do you know when something is good?
- **Ambition Trajectory** — Is what you're building getting harder over time?
- **Visibility** — Are you making your thinking available to others?

Plus an **Impact Moments** milestone tracker for when your work lands.

### Automated Workflows (2 Recipes)
- **weekly-retrospective** — Run weekly. Chains session analysis → journal ingest → coaching evaluation → written report with growth chart.
- **session-nudge** — Run at session start. One line, one intention, based on your latest report.

### Coaching Agent
- **coaching-agent** — Evaluates your sessions against the growth framework. Produces qualitative observations grounded in evidence.

## Quick Start

```
"Run the weekly retrospective recipe"
"Give me my session nudge"
```

## Weekly Time Commitment

5-10 minutes: run the retrospective (~2 min), read the letter (~2 min), glance at your growth chart (~30 sec), optionally add journal entries (~1-2 min).

---

@builders-mirror:context/growth-framework.md
```

### Step 7: Write the failing test for bundle structure

Create `amplifier-builders-mirror/tests/test_bundle_structure.py`:
```python
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
    assert bundle.get("name") == "builders-mirror", (
        f"Expected name 'builders-mirror', got {bundle.get('name')}"
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
```

### Step 8: Install dev dependencies and run tests

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
pip install pyyaml pytest ruff
```

Then run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
pytest tests/test_bundle_structure.py -v
```
Expected: ALL PASS (6 tests). The bundle.md already exists from step 6, and all directories were created in step 1.

### Step 9: Commit

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
git add -A
git commit -m "feat: scaffold bundle with manifest, toolchain, and structure tests"
```

---

## Task 2: Growth Framework Context File

Create the detailed growth framework — the "constitution" that every other component references. Defines all 5 dimensions with qualitative levels plus Impact Moments.

**Files:**
- Create: `amplifier-builders-mirror/context/growth-framework.md`
- Create: `amplifier-builders-mirror/tests/test_growth_framework.py`

**Depends on:** Task 1 (scaffold exists)

### Step 1: Write the failing test for framework completeness

Create `amplifier-builders-mirror/tests/test_growth_framework.py`:
```python
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
    assert FRAMEWORK_PATH.is_file(), (
        f"context/growth-framework.md not found at {FRAMEWORK_PATH}"
    )


def test_all_five_dimensions_present():
    """The framework must define all five growth dimensions."""
    text = FRAMEWORK_PATH.read_text()
    for dimension in REQUIRED_DIMENSIONS:
        assert dimension in text, (
            f"Dimension '{dimension}' not found in growth-framework.md"
        )


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
```

### Step 2: Run tests to verify they fail

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
pytest tests/test_growth_framework.py -v
```
Expected: FAIL — `context/growth-framework.md` does not exist yet.

### Step 3: Create the growth framework context file

Create `amplifier-builders-mirror/context/growth-framework.md`:
```markdown
# Builder's Mirror Growth Framework

This document defines the five dimensions that determine what makes someone an invaluable AI builder, plus the Impact Moments milestone tracker. The coaching agent uses this framework to evaluate sessions and journal entries. Every observation must map to a specific dimension and be grounded in evidence.

These dimensions are **role-agnostic**. Not "what makes a PM good at AI" or "what makes an engineer good at AI" — what makes *anyone* an invaluable AI builder.

---

## Problem Selection

**What it measures:** Are you choosing to work on things that matter? Not what's easy or assigned — what's important, novel, or high-impact. The quality of problems you choose to solve is the single strongest predictor of your trajectory.

**Observable from:** What you choose to build, session over session. Is it getting more ambitious, more novel, or staying comfortable? Are you picking problems that others haven't identified yet?

**Qualitative Levels:**

- **Low:** Only works on tutorials, prescribed tasks, or things that have obvious step-by-step solutions. Avoids choosing what to build.
- **Emerging:** Chooses own projects but stays in comfort zone. Builds variations of things already built. Projects are safe — unlikely to fail, but also unlikely to matter.
- **Developing:** Tackles novel problems, occasionally ambitious. Starts to identify problems worth solving rather than just interesting ones. Some projects have real users or stakes.
- **Strong:** Consistently selects high-impact, non-obvious problems. Sees problems others overlook. Builds things that change how other people work. Willing to work on hard things that might not succeed.
- **Exceptional:** Identifies problems others haven't seen yet. Creates new categories of solutions. The problems you choose to work on influence what other builders think is possible.

---

## Leverage Ratio

**What it measures:** How much output per unit of input? Can a 2-sentence prompt produce something substantial? Are you getting better at directing AI, or are you still doing most of the work yourself? This is about working *with* AI effectively, not just using AI tools.

**Observable from:** Iteration count, time-to-result, how much you accomplish per session. Are you getting more leveraged over time? Do you accomplish in one session what used to take three?

**Qualitative Levels:**

- **Low:** High iteration count for simple tasks. Micromanages the AI. Rewrites AI output manually instead of improving prompts. Sessions produce little relative to time spent.
- **Emerging:** Starting to get reasonable output from AI, but still over-iterates. Occasionally achieves high leverage on familiar tasks. Doesn't yet transfer leverage patterns across domains.
- **Developing:** Consistent leverage on standard tasks. Starting to develop reusable patterns (prompt templates, workflows, bundle composition). Some sessions show remarkable output-to-input ratios.
- **Strong:** Routinely accomplishes substantial work in few exchanges. Has internalized patterns for directing AI. Builds tools and workflows that multiply leverage for future sessions. Others would be surprised at what gets done in one session.
- **Exceptional:** Operates at extraordinary leverage — minimal input, maximum meaningful output. Creates leverage for others (tools, patterns, frameworks that make everyone more effective). The leverage compounds session over session.

---

## Taste

**What it measures:** Do you know when something is good? Do you refine and iterate toward quality, or accept the first thing that works? Taste is the irreducibly human layer — the ability to judge quality, coherence, and craft that no amount of AI capability replaces.

**Observable from:** Whether you iterate toward quality, go back and improve past work, or just accept first output. Do you refactor? Do you revisit and polish? Do you have opinions about how things should feel, not just whether they function?

**Qualitative Levels:**

- **Low:** Accepts first output that compiles or runs. No iteration toward quality. Cannot articulate why one solution is better than another. Ships without reviewing.
- **Emerging:** Sometimes iterates on output quality. Starting to develop opinions about code style, UX, or writing quality. Inconsistent — sometimes refines, sometimes ships rough.
- **Developing:** Has clear quality standards and usually meets them. Refactors and polishes. Can articulate what makes something good. Starts to develop a recognizable style or standard.
- **Strong:** Consistently produces polished output. Strong opinions about quality backed by reasoning. Goes back to improve past work. The gap between "works" and "good" matters deeply. Others recognize and trust your quality judgment.
- **Exceptional:** Defines quality standards others adopt. Taste is a competitive advantage — your work is recognizably excellent. You see quality dimensions others miss. Your judgment about what's good influences your community.

---

## Ambition Trajectory

**What it measures:** Is what you're building getting harder and more interesting over time? This is about the trajectory, not the current position. Someone building progressively harder things is more interesting than someone who's always been at the same level, even a high one.

**Observable from:** Project complexity over time, scope of what you attempt. Moving from building for yourself to building things that change how others work. Moving from following patterns to creating new ones.

**Qualitative Levels:**

- **Low:** Flat trajectory. Projects stay at roughly the same complexity. No evidence of stretching or attempting harder things. Comfortable.
- **Emerging:** Occasional stretch projects, but returns to comfort zone. Ambition comes in bursts rather than sustained growth. Some projects are harder than last month's, but the trend is inconsistent.
- **Developing:** Clear upward trajectory. Each month's projects are more ambitious than the last. Starts to scope larger efforts. Willing to fail on ambitious attempts rather than always succeeding on easy ones.
- **Strong:** Sustained ambitious trajectory. Regularly attempts things at the edge of what's possible. Scope has grown from personal tools to things that affect others. Comfortable with the discomfort of hard problems.
- **Exceptional:** Redefining what's possible. Building at a scope or complexity that others consider out of reach. The trajectory itself inspires others. Not just building harder things — building things in harder categories.

---

## Visibility

**What it measures:** Are you making your thinking and building available to others? This is a **leading indicator** — the behavior that creates the conditions for impact. You can build incredible things in silence, but if nobody knows, nobody benefits and nobody hires you.

**Observable from:** Self-reported entries about publishing, sharing, writing, contributing to communities. This dimension relies heavily on journal entries since Amplifier sessions don't capture external sharing.

**Qualitative Levels:**

- **Low:** Builds in complete isolation. No sharing, no publishing, no community participation. Work exists only on local machine.
- **Emerging:** Occasional sharing — a tweet, a message in a community channel. Inconsistent. Sharing feels uncomfortable or forced.
- **Developing:** Regular sharing cadence. Publishes blog posts, contributes to communities, shares work-in-progress. Starting to build a recognizable presence.
- **Strong:** Consistent and strategic visibility. Writes about what you're learning, publishes tools for others, actively participates in communities. People know your work. You're becoming a reference point in your domain.
- **Exceptional:** Your visibility creates gravity. People seek out your thinking. You influence the conversation about how AI builders work. Writing, publishing, and sharing are integrated into your workflow, not separate from it.

---

## Impact Moments

Impact is a **lagging indicator** — someone using your tool, adopting your pattern, or giving you feedback might take weeks to happen. So Impact Moments live outside the five weekly dimensions as a milestone log.

The split: **Visibility** (leading indicator) tracks the *behavior* that creates impact. **Impact Moments** (lagging indicator) tracks when impact actually *lands*.

**What gets tracked:**
- Someone uses a tool or pattern you created
- You receive meaningful feedback on your work
- Someone adopts an approach you published
- Your work is referenced, cited, or built upon
- You're invited to contribute because of your visible work

**How it's tracked:**
- Self-reported in the growth journal (e.g., "someone used my bundle in production")
- The coaching agent asks about Impact Moments during the weekly retrospective
- Celebrated in the weekly letter when they happen
- Noticed when absent: "You've been building great stuff but nobody knows about it. What's one thing you could share this week?"

---

## How the Coaching Agent Uses This Framework

1. **Map evidence to dimensions.** Every observation must cite a specific session, journal entry, or pattern. Never make claims without evidence.
2. **Use qualitative levels, not numeric scores.** Say "your Problem Selection is at the Developing level" — not "your Problem Selection is 3/5."
3. **Focus on trajectory, not position.** "You moved from Emerging to Developing this month" is more useful than "you are at Developing."
4. **Acknowledge cold starts.** On the first week with no history, focus on the journal and stated intentions. Don't fabricate observations.
5. **Be specific, not generic.** "You built X this week — that's more ambitious than Y" is good. "Keep pushing yourself" is useless.
```

### Step 4: Run tests to verify they pass

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
pytest tests/test_growth_framework.py -v
```
Expected: ALL PASS (6 tests).

### Step 5: Commit

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
git add -A
git commit -m "feat: add growth framework context with 5 dimensions and qualitative levels"
```

---

## Task 3: Coaching Agent

Create the coaching agent — the central intelligence that evaluates sessions and journal entries against the growth framework. This is the most critical artifact in the bundle.

**Files:**
- Create: `amplifier-builders-mirror/agents/coaching-agent.md`
- Create: `amplifier-builders-mirror/tests/test_coaching_agent.py`

**Depends on:** Task 2 (growth framework exists)

### Step 1: Write the failing test for agent structure

Create `amplifier-builders-mirror/tests/test_coaching_agent.py`:
```python
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
        "Agent must reference @builders-mirror:context/growth-framework.md"
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
```

### Step 2: Run tests to verify they fail

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
pytest tests/test_coaching_agent.py -v
```
Expected: FAIL — `agents/coaching-agent.md` does not exist yet.

### Step 3: Create the coaching agent

The frontmatter follows the pattern from `amplifier-bundle-ui-vision/agents/visual-auditor.md` and `amplifier-bundle-dev-machine/agents/admissions-advisor.md`.

Create `amplifier-builders-mirror/agents/coaching-agent.md`:
````markdown
---
meta:
  name: coaching-agent
  description: >
    Metacognitive coaching agent for AI builders. Evaluates Amplifier session
    data and growth journal entries against the Builder's Mirror growth framework
    (Problem Selection, Leverage Ratio, Taste, Ambition Trajectory, Visibility)
    plus Impact Moments. Produces qualitative observations grounded in specific
    evidence — never generic platitudes.

    <example>
    user: 'Evaluate my sessions and journal from this week'
    assistant: 'I will delegate to builders-mirror:coaching-agent to evaluate against the growth framework.'
    <commentary>Session evaluation requests trigger the coaching agent.</commentary>
    </example>
---

# Builder's Mirror Coaching Agent

You are a metacognitive coach for AI builders. You evaluate session data and journal entries against the growth framework, producing observations that are specific, evidence-based, and actionable.

## Your Knowledge

You know the growth framework intimately:

@builders-mirror:context/growth-framework.md

## Core Principles

1. **Evidence first.** Every observation must cite a specific session, journal entry, or pattern. If you can't point to evidence, don't make the claim.
2. **Qualitative, not numeric.** Use the framework's levels (Low / Emerging / Developing / Strong / Exceptional) — never assign numeric scores.
3. **Trajectory over position.** "You moved from Emerging to Developing" matters more than "You are at Developing."
4. **Honest, not harsh.** Be direct about what you see. Don't soften observations into meaninglessness. But also don't be cruel — you're a coach, not a critic.
5. **Specific, not generic.** "You built X this week — that's more ambitious than Y from last week" is good. "Keep pushing yourself" is worthless noise. Delete generic advice before it leaves your mouth.

## What You Receive

When invoked by the weekly retrospective recipe, you receive two inputs:

1. **Session Analysis** — extracted from Amplifier session logs by the session analyst. Contains: what was built, tools used, iteration counts, problems framed, completions vs. abandonments, session durations.
2. **Journal Entries** — from the growth journal, covering self-reported events the sessions can't see: things published, feedback received, conversations, intentions.

## How You Evaluate

For each of the five dimensions, follow this process:

### Problem Selection
- Look at WHAT was built across sessions this week
- Compare to previous weeks (if history available): is complexity increasing?
- Check journal for context on why these problems were chosen
- Assess: are these safe/comfortable problems, or ambitious/novel ones?

### Leverage Ratio
- Look at iteration counts and session efficiency
- How much was accomplished per session relative to effort?
- Are there patterns of over-iteration (many attempts at simple tasks)?
- Compare to previous weeks: is leverage improving?

### Taste
- Look for evidence of iteration toward quality (not just getting things to work)
- Did the builder go back and refine, refactor, or polish?
- Did they accept first outputs or push for better?
- Check journal for stated quality intentions

### Ambition Trajectory
- Compare this week's project scope to previous weeks
- Is complexity increasing over time?
- Are they attempting things at the edge of their ability?
- Check journal for goals and stretch intentions

### Visibility
- Primarily from journal entries (sessions don't capture external sharing)
- Did they publish, write, or share anything?
- Did they contribute to communities?
- If no visibility entries: note this specifically

### Impact Moments
- Check journal for impact signals: someone used their tool, gave feedback, adopted their pattern
- If present: celebrate it specifically in your evaluation
- If absent after several weeks of visibility: note the gap gently

## Cold Start Handling

On the **first week** (no previous reports exist, no history to compare against):

- Acknowledge the cold start explicitly: "This is your first week, so I'm establishing your baseline rather than tracking trajectory."
- Focus on journal entries and stated intentions
- Assess current levels based on available evidence only
- Do NOT fabricate observations or comparisons
- Do NOT pretend to have history that doesn't exist
- Frame the evaluation as "here's where you're starting from" not "here's how you're doing"

## Output Format

Structure your evaluation as follows. The writer agent downstream consumes this format.

```
## Coaching Evaluation — Week of [DATE]

### This Week's Evidence
[Brief summary of what happened — sessions and journal combined]

### Dimension Assessments

**Problem Selection: [Level]**
[2-3 sentences with specific evidence. What was built, how it compares to prior weeks.]

**Leverage Ratio: [Level]**
[2-3 sentences with specific evidence. Session efficiency, iteration patterns.]

**Taste: [Level]**
[2-3 sentences with specific evidence. Quality iteration, refinement patterns.]

**Ambition Trajectory: [Level]**
[2-3 sentences with specific evidence. Complexity trend over time.]

**Visibility: [Level]**
[2-3 sentences with specific evidence. What was shared, published, contributed.]

### Impact Moments
[Any impact events from the journal. Or note their absence.]

### Key Observation
[One insight that cuts across dimensions — the most important thing to understand about this week]

### Suggested Focus for Next Week
[One specific, actionable thing to try. Not generic — tied to this week's evidence.]
```

---

@foundation:context/shared/common-agent-base.md
````

### Step 4: Run tests to verify they pass

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
pytest tests/test_coaching_agent.py -v
```
Expected: ALL PASS (7 tests).

### Step 5: Commit

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
git add -A
git commit -m "feat: add coaching agent with growth framework evaluation logic"
```

---

## Task 4: Weekly Retrospective Recipe

Create the core product — the 4-step chain recipe that runs weekly.

**Files:**
- Create: `amplifier-builders-mirror/recipes/weekly-retrospective.yaml`
- Create: `amplifier-builders-mirror/tests/test_recipe_schema.py`

**Depends on:** Task 3 (coaching agent exists)

### Step 1: Write the failing test for recipe validation

Create `amplifier-builders-mirror/tests/test_recipe_schema.py`:
```python
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
        f"Expected 4 steps (session-analyst, journal-ingest, coaching, writer), "
        f"got {len(steps)}"
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
```

### Step 2: Run tests to verify they fail

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
pytest tests/test_recipe_schema.py -v
```
Expected: FAIL — recipe files don't exist yet. The session-nudge tests will also fail (that's fine — they'll pass after Task 5).

### Step 3: Create the weekly retrospective recipe

The recipe YAML follows the pattern from `amplifier-bundle-stories/recipes/weekly-digest.yaml` and `amplifier-change-advisor/recipes/pr-review.yaml`.

Create `amplifier-builders-mirror/recipes/weekly-retrospective.yaml`:
```yaml
name: weekly-retrospective
description: >
  Weekly coaching pipeline for AI builders. Chains four agents:
  session analysis → journal ingest → coaching evaluation → written report.
  Produces a weekly letter with growth chart saved to data/reports/.
version: "0.1.0"
tags: ["coaching", "retrospective", "growth", "weekly"]

# Usage:
#   "Run the weekly retrospective recipe"
#   amplifier tool invoke recipes operation=execute recipe_path=@builders-mirror:recipes/weekly-retrospective.yaml

context:
  # Override the week ending date (default: today)
  week_ending: ""
  # Path to growth journal
  journal_path: "data/growth-journal.md"
  # Directory for report output
  reports_dir: "data/reports"

steps:
  # ==========================================================================
  # Step 1: Session Analysis — mine Amplifier session logs from the past week
  # ==========================================================================
  - id: session-analysis
    agent: "foundation:story-researcher"
    timeout: 600
    output: session_data
    prompt: |
      ANALYZE MODE.

      Analyze Amplifier session logs from the past 7 days{% if week_ending != "" %} ending {{week_ending}}{% endif %}.

      Look for session files in:
      - ~/.amplifier/sessions/
      - .amplifier/sessions/

      For each session, extract:
      1. **What was built** — projects, features, artifacts created
      2. **Tools used** — which tools/functions were called and how often
      3. **Iteration count** — how many user prompts per session (proxy for efficiency)
      4. **Problem framing** — how problems were described and scoped
      5. **Completions vs. abandonments** — what was finished, what was dropped
      6. **Session duration** — time from first to last event

      Structure your output as:

      ## Session Summary — Week of [DATE]

      **Sessions analyzed:** [count]
      **Total time:** [estimate]

      ### Session-by-Session Breakdown
      For each session:
      - Date and duration
      - What was built
      - Tool usage summary
      - Iteration count
      - Outcome (completed / in-progress / abandoned)

      ### Patterns Observed
      - What types of problems were worked on
      - How efficient sessions were
      - Any notable trends (e.g., sessions getting shorter/longer, more/less complex)

      If no session data is available, report that clearly. The coaching agent
      downstream handles the cold start case.

  # ==========================================================================
  # Step 2: Journal Ingest — read self-reported growth journal entries
  # ==========================================================================
  - id: journal-ingest
    timeout: 300
    output: journal_data
    prompt: |
      Read the growth journal at {{journal_path}} and extract entries from the
      past 7 days{% if week_ending != "" %} ending {{week_ending}}{% endif %}.

      The journal is free-form markdown with date headers. Entries may include:
      - Things published or shared (Visibility dimension)
      - Feedback or adoption signals (Impact Moments)
      - Conversations or insights not in session logs
      - Intentions or goals for upcoming work

      Merge with the session analysis data:

      {{session_data}}

      Produce a combined weekly evidence summary:

      ## Combined Weekly Evidence

      ### From Sessions (Automated)
      [Summarize key session findings]

      ### From Journal (Self-Reported)
      [Summarize journal entries, or note if journal was empty]

      ### Evidence Gaps
      [Note what's missing — e.g., "No journal entries about sharing or visibility this week"]

      If the journal file doesn't exist or has no recent entries, note that
      clearly. The coaching agent handles empty journal data.

  # ==========================================================================
  # Step 3: Coaching Evaluation — assess against the growth framework
  # ==========================================================================
  - id: coaching-evaluation
    agent: "builders-mirror:coaching-agent"
    timeout: 600
    output: coaching_output
    prompt: |
      Evaluate this week's combined evidence against the growth framework.

      {{journal_data}}

      Check for previous weekly reports in {{reports_dir}}/ to understand
      trajectory and compare to prior weeks. If no previous reports exist,
      this is a cold start — follow your cold start handling instructions.

      Produce your evaluation in the output format defined in your instructions.

  # ==========================================================================
  # Step 4: Write Report — produce the weekly letter + growth chart
  # ==========================================================================
  - id: write-report
    agent: "foundation:technical-writer"
    timeout: 600
    output: weekly_report
    prompt: |
      You are writing the Builder's Mirror weekly report. This is a personal
      letter TO the builder, ABOUT their week. Think Sam Schillace's Sunday
      Letters but written to one person about their specific growth.

      Here is the coaching evaluation:

      {{coaching_output}}

      Write a weekly report with TWO parts and save it as a markdown file.

      ## Part 1: The Letter

      Tone: conversational, honest, specific. Like a thoughtful mentor who
      watched you work all week. NOT a report card. NOT a performance review.

      Include:
      - What you actually did this week (the facts — brief)
      - How you're tracking on each dimension (the mirror — this is the core)
      - One specific thing to try next week (the nudge — from the coaching eval)
      - Your trajectory over time if history exists ("this is week N, here's how you've changed")
      - Impact Moments celebration if any happened

      ## Part 2: The Growth Chart

      Render a text-based radar chart showing the five dimensions and their
      current qualitative levels. Use this exact format:

      ```
      === YOUR BUILDER SHAPE ===

                   Problem Selection
                        [LEVEL]
                          |
                          |
      Visibility ----+----+----+---- Leverage Ratio
        [LEVEL]      |    |    |       [LEVEL]
                     |    |    |
                     +----+----+
                    /           \
                   /             \
          Ambition               Taste
        Trajectory              [LEVEL]
          [LEVEL]
      ```

      Replace [LEVEL] with the actual qualitative level from the coaching
      evaluation (Low / Emerging / Developing / Strong / Exceptional).

      If previous reports exist, also show the change:
      ```
      Problem Selection: Developing → Strong ▲
      Leverage Ratio:    Emerging (no change) →
      Taste:             Developing (no change) →
      Ambition:          Low → Emerging ▲
      Visibility:        Low (no change) →
      ```

      ## Save the Report

      Save the complete report (letter + chart) to:
      {{reports_dir}}/week-of-[YYYY-MM-DD].md

      Use the Monday date of the current week for the filename.

      After saving, output the full report content so the user can read it
      immediately.
```

### Step 4: Run the weekly retrospective tests

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
pytest tests/test_recipe_schema.py::test_weekly_retrospective_exists tests/test_recipe_schema.py::test_weekly_retrospective_has_required_top_level_fields tests/test_recipe_schema.py::test_weekly_retrospective_has_four_steps tests/test_recipe_schema.py::test_weekly_retrospective_step_ids tests/test_recipe_schema.py::test_weekly_retrospective_steps_have_required_fields tests/test_recipe_schema.py::test_weekly_retrospective_coaching_step_uses_coaching_agent -v
```
Expected: ALL PASS (6 weekly-retrospective tests). The 2 session-nudge tests will still fail — that's expected until Task 5.

### Step 5: Commit

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
git add -A
git commit -m "feat: add weekly retrospective recipe with 4-step coaching pipeline"
```

---

## Task 5: Session-Start Nudge Recipe

Create the lightweight recipe that produces a single-line intention at the start of a session.

**Files:**
- Create: `amplifier-builders-mirror/recipes/session-nudge.yaml`

**Depends on:** Task 4 (weekly retrospective exists — the nudge reads its output)

### Step 1: Verify the session-nudge tests are currently failing

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
pytest tests/test_recipe_schema.py::test_session_nudge_exists tests/test_recipe_schema.py::test_session_nudge_has_required_fields -v
```
Expected: FAIL — `session-nudge.yaml` does not exist yet.

### Step 2: Create the session-nudge recipe

Create `amplifier-builders-mirror/recipes/session-nudge.yaml`:
```yaml
name: session-nudge
description: >
  Lightweight session-start nudge. Reads the most recent weekly report and
  produces a single-line intention for this session. One line, one intention,
  then get out of the way.
version: "0.1.0"
tags: ["coaching", "nudge", "session-start"]

# Usage:
#   "Give me my session nudge"
#   amplifier tool invoke recipes operation=execute recipe_path=@builders-mirror:recipes/session-nudge.yaml

context:
  reports_dir: "data/reports"

steps:
  # ==========================================================================
  # Step 1: Read latest report and produce one-line nudge
  # ==========================================================================
  - id: nudge
    agent: "builders-mirror:coaching-agent"
    timeout: 120
    output: session_nudge
    prompt: |
      NUDGE MODE — you are producing a session-start intention, not a full evaluation.

      Read the most recent weekly report from {{reports_dir}}/ (the file with
      the latest date in its filename).

      Based on the report's coaching evaluation, produce EXACTLY ONE LINE —
      a specific, actionable intention for this session.

      Rules:
      - ONE line. Not two. Not a paragraph. One sentence.
      - Must be specific to what the report said (not generic motivation)
      - Must be actionable TODAY in THIS session
      - Tone: direct, confident, like a coach's whisper before the game

      Good examples:
      - "Last week your leverage ratio was flat. Today, try to accomplish something meaningful in under 3 exchanges."
      - "You haven't started anything new in 2 weeks. Today, pick a problem you've never worked on."
      - "You abandoned your last project after one session. Today, go back and finish it."

      Bad examples (DO NOT produce these):
      - "Keep up the good work!" (generic, not actionable)
      - "Today, focus on improving your skills." (vague, not specific)
      - Any multi-sentence response

      If no previous report exists (first session), produce:
      "First session — just build something. We'll start tracking next week."

      Output ONLY the single line. Nothing else.
```

### Step 3: Run all recipe tests

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
pytest tests/test_recipe_schema.py -v
```
Expected: ALL PASS (8 tests — 6 for weekly-retrospective + 2 for session-nudge).

### Step 4: Commit

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
git add -A
git commit -m "feat: add session-start nudge recipe (single-line intention)"
```

---

## Task 6: Growth Journal and Report Storage

Create the growth journal template that users will edit, and set up the report storage structure.

**Files:**
- Create: `amplifier-builders-mirror/data/growth-journal.md`

**Depends on:** Task 1 (scaffold — `data/reports/` directory already exists)

### Step 1: Create the growth journal template

Create `amplifier-builders-mirror/data/growth-journal.md`:
```markdown
# Growth Journal

This is your self-reported growth journal for Builder's Mirror. Add entries here for things that Amplifier session logs can't see — sharing, publishing, feedback, conversations, intentions, and impact moments.

**How to use:** Add entries under a date header. Free-form — write whatever feels relevant. The coaching agent reads natural language.

**What to log:**
- Things you published or shared (blog posts, tools, community contributions)
- Feedback or adoption signals (someone used your tool, gave feedback)
- Conversations or insights not captured in sessions
- Intentions or goals ("this week I want to focus on X")
- Impact moments (someone used something you built)

**What NOT to log:** Anything already in your Amplifier sessions. The tool handles that automatically.

---

## 2026-03-11

_Start logging here. Replace this with your first entry._
```

### Step 2: Verify the reports directory and gitkeep exist

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
test -d data/reports && test -f data/reports/.gitkeep && echo "PASS: reports directory ready" || echo "FAIL: reports directory missing"
```
Expected: `PASS: reports directory ready`

### Step 3: Commit

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
git add -A
git commit -m "feat: add growth journal template and report storage structure"
```

---

## Task 7: Growth Chart Validation Tests

The growth chart is already embedded in the weekly retrospective recipe's writer step (Task 4, Step 3 — the `write-report` step includes the text-based radar chart format). This task verifies it's correct and adds dedicated tests.

**Files:**
- Modify: `amplifier-builders-mirror/tests/test_recipe_schema.py` (add chart tests)

**Depends on:** Task 4 (weekly retrospective recipe exists)

### Step 1: Add growth chart tests

Append these tests to the bottom of `amplifier-builders-mirror/tests/test_recipe_schema.py`:

```python

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
```

### Step 2: Run all tests

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
pytest tests/ -v
```
Expected: ALL PASS (all tests across all 4 test files).

### Step 3: Commit

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
git add -A
git commit -m "feat: add growth chart validation tests"
```

---

## Task 8: Copy Design and Plan Documents

Copy the design document and this implementation plan into the project's docs directory so the dev-machine admissions process can find them.

**Files:**
- Copy: `docs/plans/2026-03-11-builders-mirror-design.md` → `amplifier-builders-mirror/docs/plans/`
- Copy: `docs/plans/2026-03-11-builders-mirror-implementation.md` → `amplifier-builders-mirror/docs/plans/`

### Step 1: Copy the documents

Run:
```bash
cd /Users/chrispark/Projects
cp docs/plans/2026-03-11-builders-mirror-design.md amplifier-builders-mirror/docs/plans/
cp docs/plans/2026-03-11-builders-mirror-implementation.md amplifier-builders-mirror/docs/plans/
```

### Step 2: Verify

Run:
```bash
ls -la /Users/chrispark/Projects/amplifier-builders-mirror/docs/plans/
```
Expected: Both files present.

### Step 3: Final test run

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
pytest tests/ -v
```
Expected: ALL PASS — every test in the project passes.

### Step 4: Commit

Run:
```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror
git add -A
git commit -m "docs: add design and implementation plan documents"
```

---

## Final Verification Checklist

Before running dev-machine `/admissions`, verify:

```bash
cd /Users/chrispark/Projects/amplifier-builders-mirror

# 1. All tests pass
pytest tests/ -v

# 2. All required files exist
ls bundle.md pyproject.toml .gitignore
ls agents/coaching-agent.md
ls context/growth-framework.md
ls recipes/weekly-retrospective.yaml recipes/session-nudge.yaml
ls data/growth-journal.md data/reports/.gitkeep
ls tests/test_bundle_structure.py tests/test_recipe_schema.py tests/test_coaching_agent.py tests/test_growth_framework.py
ls docs/plans/2026-03-11-builders-mirror-design.md docs/plans/2026-03-11-builders-mirror-implementation.md

# 3. Git is clean
git status

# 4. Git log shows all commits
git log --oneline
```

### Expected git log:
```
xxxxxxx docs: add design and implementation plan documents
xxxxxxx feat: add growth chart validation tests
xxxxxxx feat: add growth journal template and report storage structure
xxxxxxx feat: add session-start nudge recipe (single-line intention)
xxxxxxx feat: add weekly retrospective recipe with 4-step coaching pipeline
xxxxxxx feat: add coaching agent with growth framework evaluation logic
xxxxxxx feat: add growth framework context with 5 dimensions and qualitative levels
xxxxxxx feat: scaffold bundle with manifest, toolchain, and structure tests
```

### Dev-Machine Admissions Gate Readiness:

| Gate | What It Checks | Status |
|------|---------------|--------|
| **1. Decomposability** | Can the project be broken into discrete features? | Ready — 8 tasks, each independently testable |
| **2. Verifiable Correctness** | Can tests prove things work? | Ready — 4 test files, 24+ assertions |
| **3. Sufficient Architecture** | Is there an architecture document? | Ready — Design doc + implementation plan in `docs/plans/` |
| **4. Functioning Toolchain** | Do build/test commands work? | Ready — `pytest tests/ -v` runs clean |
| **5. Spec Quality** | Can you write machine-quality specs? | Ready — Implementation plan has exact file paths, code, and expected outputs |
