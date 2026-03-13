# Session History Analyzer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the session history analyzer invocable as an app bundle — user says "analyze my sessions" and gets a coaching evaluation from session data alone.

**Architecture:** Fix bundle structure (4 prerequisites), update coaching agent for on-demand session-only evaluation, create a 2-step recipe (evidence gathering + coaching evaluation).

**Tech Stack:** Amplifier bundle YAML, agent markdown, pytest, Python 3.11+

**Design doc:** `docs/plans/2026-03-12-session-history-analyzer-design.md`

---

## Task 1: Add recipes bundle include

The recipes tool cannot execute without `amplifier-bundle-recipes` in the bundle includes. This unblocks all recipe work.

**Files:**
- Modify: `bundle.md` (line 12 area)

**Step 1: Write the failing test**

Add a test to `tests/test_bundle_structure.py` that verifies the recipes bundle is included:

```python
def test_bundle_includes_recipes_bundle(bundle_frontmatter):
    """The bundle must include amplifier-bundle-recipes for recipe execution."""
    includes = bundle_frontmatter.get("includes", [])
    sources = [inc.get("bundle", "") for inc in includes if isinstance(inc, dict)]
    assert any("amplifier-bundle-recipes" in s for s in sources), (
        "bundle.md must include amplifier-bundle-recipes in includes"
    )
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_bundle_structure.py::test_bundle_includes_recipes_bundle -v`
Expected: FAIL — recipes bundle not currently in includes

**Step 3: Fix bundle.md**

Edit `bundle.md` — add the recipes bundle after the foundation include (after line 12):

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/microsoft/amplifier-bundle-recipes@main
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_bundle_structure.py::test_bundle_includes_recipes_bundle -v`
Expected: PASS

**Step 5: Run full suite**

Run: `uv run pytest tests/ -v`
Expected: All passing (318+ tests)

**Step 6: Commit**

```
feat(bundle): add recipes bundle include — unblocks recipe execution
```

---

## Task 2: Fix double-load of growth-framework.md

The growth framework is loaded twice — via `context.include` in bundle.md YAML AND via `@mention` in coaching-agent.md. Drop the YAML entry, keep the @mention.

**Files:**
- Modify: `bundle.md` (lines 17-19)

**Step 1: Write the failing test**

Add to `tests/test_bundle_structure.py`:

```python
def test_growth_framework_not_in_context_include(bundle_frontmatter):
    """Growth framework should be loaded via @mention only, not context.include."""
    context = bundle_frontmatter.get("context", {})
    includes = context.get("include", [])
    framework_refs = [i for i in includes if "growth-framework" in str(i)]
    assert len(framework_refs) == 0, (
        "growth-framework.md should not be in context.include — "
        "it is already @mentioned in coaching-agent.md"
    )
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_bundle_structure.py::test_growth_framework_not_in_context_include -v`
Expected: FAIL — growth-framework.md currently in context.include

**Step 3: Remove the context.include block from bundle.md**

Delete lines 17-19 from `bundle.md`:
```yaml
context:
  include:
    - builder-coach:context/growth-framework.md
```

The `@mention` on line 60 of bundle.md body and line 26 of coaching-agent.md remain — that's the correct single load path.

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_bundle_structure.py::test_growth_framework_not_in_context_include -v`
Expected: PASS

**Step 5: Run full suite**

Run: `uv run pytest tests/ -v`
Expected: All passing

**Step 6: Commit**

```
fix(bundle): remove double-load of growth-framework — keep @mention only
```

---

## Task 3: Create coach-instructions context file

The AI needs to know what recipes exist and how to invoke them. Without this, natural language requests like "analyze my sessions" can't be dispatched to the right recipe.

**Files:**
- Create: `context/coach-instructions.md`
- Modify: `bundle.md` (add context @mention in body)

**Step 1: Write the failing test**

Add to `tests/test_bundle_structure.py`:

```python
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
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_bundle_structure.py::test_coach_instructions_file_exists -v`
Expected: FAIL — file does not exist

**Step 3: Create the file**

Create `context/coach-instructions.md`:

```markdown
# Builder Coach — Available Workflows

You are operating as part of the Builder Coach bundle. Here are the workflows users can invoke:

## Session History Analyzer

Analyze the user's Amplifier session history and produce a coaching evaluation against the 5-dimension growth framework. Works purely from session data — no journal input required.

**Invoke:** `@builder-coach:recipes/session-history-analyzer.yaml`

**When the user says:** "analyze my sessions", "how am I doing", "run the session analyzer", "give me a coaching evaluation", "evaluate my growth"

## Session Nudge

One-line session-start intention based on the latest coaching report. Quick, actionable, dimension-specific.

**Invoke:** `@builder-coach:recipes/session-nudge.yaml`

**When the user says:** "give me my nudge", "what should I focus on today", "session nudge"

## Weekly Retrospective

Full coaching pipeline with journal integration. Chains session analysis, journal ingest, coaching evaluation, and report writing. Use when the user has both session data AND journal entries.

**Invoke:** `@builder-coach:recipes/weekly-retrospective.yaml`

**When the user says:** "run the weekly retrospective", "weekly retro", "full coaching report with journal"
```

Then add `@builder-coach:context/coach-instructions.md` to the markdown body of `bundle.md` (before the growth framework @mention).

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_bundle_structure.py -v`
Expected: All passing

**Step 5: Commit**

```
feat(bundle): add coach-instructions context for recipe dispatch
```

---

## Task 4: Update coaching agent — on-demand session-only evaluation

This is the core change. The coaching agent needs to shift from "weekly + journal" framing to "on-demand + session-data-first" evaluation.

**Files:**
- Modify: `agents/coaching-agent.md`

**Step 1: Write the failing tests**

Add to `tests/test_coaching_agent.py`:

```python
def test_coaching_agent_supports_session_only_evaluation(agent_content):
    """Agent must describe session-only evaluation path."""
    assert "session data" in agent_content.lower() or "session history" in agent_content.lower()


def test_coaching_agent_visibility_not_journal_only(agent_content):
    """Visibility must be evaluable from session data, not journal-only."""
    vis_section = _extract_section(agent_content, "### Visibility")
    assert "primarily from journal" not in vis_section.lower(), (
        "Visibility section must not say 'primarily from journal' — "
        "it should describe session-data signals"
    )


def test_coaching_agent_on_demand_framing(agent_content):
    """Output format must not be hardcoded to weekly framing."""
    assert "Week of [DATE]" not in agent_content, (
        "Output format should use scope-aware framing, not 'Week of [DATE]'"
    )


def test_coaching_agent_signal_transparency(agent_content):
    """Agent must describe signal strength / confidence calibration."""
    lower = agent_content.lower()
    assert "signal" in lower or "confidence" in lower or "calibrat" in lower, (
        "Agent must describe how to calibrate evaluation to available signal"
    )
```

Note: `_extract_section` is a helper that pulls text between a heading and the next heading of equal or higher level. Check if it exists in the test file already; if not, add it.

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_coaching_agent.py -v`
Expected: At least 3 FAIL (visibility journal-only, weekly framing, signal transparency)

**Step 3: Update the coaching agent**

Edit `agents/coaching-agent.md` with the following changes:

**a) Update description (frontmatter, lines 4-9):**
Replace with on-demand framing. Remove "weekly" references. Add session-only capability.

**b) Update "What You Receive" (lines 37-41):**
Replace with two invocation paths:
- **Via Session History Analyzer recipe:** receives pre-structured evidence markdown with all sessions, historical trends, and last-report boundary
- **Via Weekly Retrospective recipe:** receives session analysis + journal entries (existing path)

**c) Update Visibility section (lines 72-75):**
Replace "Primarily from journal entries" with session-data signals:
- Did they write documentation, READMEs, or blog posts?
- Did they work on public-facing content?
- Did they build things designed for others to use?
- Did they create talks, tutorials, or instructional content?
- If no visibility signals found in session data, note the gap and suggest journal entries as an upgrade

**d) Update Cold Start Handling (lines 82-91):**
Replace week-scoped cold start with scope-aware handling:
- **First run (no prior reports):** Baseline mode — assess current levels from all available sessions. Frame as "establishing your baseline" with honest confidence hedging.
- **Returning user:** Delta mode — everything since last report is new evidence; compare against established baseline.
- **Thin data (< 3 sessions):** Acknowledge limited signal, evaluate what's visible, be transparent: "Based on 2 sessions, I can see early patterns but the picture is preliminary."
- **Rich data (20+ sessions):** Full-confidence evaluation with pattern identification.

**e) Update Output Format (lines 93-128):**
Change `## Coaching Evaluation — Week of [DATE]` to:
```
## Coaching Evaluation — [DATE]

### Scope
[How many sessions analyzed, date range, whether this is baseline or delta mode]
```
Add signal strength indicator per dimension:
```
**Problem Selection: [Level]** (signal: strong/moderate/limited)
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_coaching_agent.py -v`
Expected: All passing

**Step 5: Run full suite**

Run: `uv run pytest tests/ -v`
Expected: All passing

**Step 6: Commit**

```
feat(coaching-agent): update for on-demand session-only evaluation

- Evaluate all 5 dimensions from session data (including Visibility)
- On-demand framing replaces weekly cadence
- Signal strength transparency per dimension
- Scope-aware cold start handling (baseline vs delta mode)
```

---

## Task 5: Create the session-history-analyzer recipe

The new recipe that ties everything together.

**Files:**
- Create: `recipes/session-history-analyzer.yaml`

**Step 1: Write the failing tests**

Add a new test file `tests/test_session_history_analyzer_recipe.py`:

```python
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
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_session_history_analyzer_recipe.py -v`
Expected: FAIL — file does not exist

**Step 3: Create the recipe**

Create `recipes/session-history-analyzer.yaml`:

```yaml
name: session-history-analyzer
description: >
  Analyze Amplifier session history and produce a coaching evaluation
  against the 5-dimension growth framework. Works purely from session
  data — no journal input required. On-demand, not calendar-locked.

version: "0.1.0"

context:
  reports_dir: "data/reports"

steps:
  - id: gather-evidence
    prompt: |
      You are a session data preprocessor. Your job is to gather and structure
      ALL available Amplifier session data for the coaching agent.

      ## Instructions

      1. **Find all session directories.** Look in these locations:
         - ~/.amplifier/sessions/
         - ~/.amplifier/projects/*/sessions/
         - .amplifier/sessions/

         Each valid session is a directory containing an `events.jsonl` file.
         List what you find — count of sessions, date range.

      2. **Check for a prior coaching report.** Look in `{{reports_dir}}/` for
         `week-of-*.md` files. If one exists, note the most recent report date.
         This is the boundary between "new evidence" and "established baseline."

      3. **Extract session summaries.** For each session's `events.jsonl`:
         - Count user and assistant messages
         - List tools used and their call counts
         - Note the first user message (session description/intent)
         - Calculate session duration from first to last timestamp
         - Note the session date

      4. **Format the evidence.** Output a structured evidence block:

         ```
         ## Session Evidence

         ### Scope
         - Sessions found: [N]
         - Date range: [earliest] to [latest]
         - Prior report: [date] or "None (first evaluation)"
         - New sessions since last report: [N] (or "all" if first run)

         ### Session Summaries
         For each session (newest first):
         - **[Date] — [First user message, truncated to 100 chars]**
           Duration: [X min] | Messages: [N user, N assistant] | Top tools: [tool1 (N), tool2 (N)]

         ### Aggregate Patterns
         - Total sessions: [N]
         - Total time: [X hours]
         - Most-used tools: [ranked list]
         - Average session duration: [X min]
         ```

      Be thorough. Include EVERY session you find. Do not filter or skip.
      The coaching agent will decide what matters.

  - id: coaching-evaluation
    agent: "builder-coach:coaching-agent"
    prompt: |
      Here is the structured evidence from the user's Amplifier session history:

      {{gather-evidence}}

      Evaluate this evidence against the growth framework. Follow your evaluation
      process for all five dimensions. Calibrate your confidence to the available
      signal. Be transparent about the scope of your analysis.

      After writing your evaluation, save the report to `{{reports_dir}}/`.
      Use today's date, normalized to Monday of the current week, as the filename:
      `week-of-YYYY-MM-DD.md`.
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_session_history_analyzer_recipe.py -v`
Expected: All passing

**Step 5: Run full suite**

Run: `uv run pytest tests/ -v`
Expected: All passing

**Step 6: Commit**

```
feat(recipe): add session-history-analyzer — on-demand coaching from session data
```

---

## Task 6: Update bundle.md description and quick start

Reflect the new session history analyzer in the bundle's user-facing documentation.

**Files:**
- Modify: `bundle.md` (lines 40-56 area)

**Step 1: Update the bundle markdown body**

- Change "2 Recipes" to "3 Recipes" (line 40 area)
- Add the session history analyzer to the recipe list
- Update quick start to lead with the analyzer (since it's the primary entry point now)
- Add the `@builder-coach:context/coach-instructions.md` mention in the body

**Step 2: Run structural tests**

Run: `uv run pytest tests/test_bundle_structure.py -v`
Expected: All passing

**Step 3: Run full suite**

Run: `uv run pytest tests/ -v`
Expected: All passing

**Step 4: Commit**

```
docs(bundle): update description and quick start for session history analyzer
```

---

## Task 7: Final verification

**Step 1: Run complete test suite**

Run: `uv run pytest tests/ -v`
Expected: All passing (318 original + new tests)

**Step 2: Run code quality checks**

Run: `uv run ruff check .` and `uv run ruff format --check .`
Expected: Clean

**Step 3: Verify git log is clean**

Run: `git log --oneline -10`
Expected: Clean commit history with 6 new commits after the design doc

**Step 4: Verify bundle can be described**

Manually check: does `bundle.md` correctly describe the full system? Does `context/coach-instructions.md` list all three recipes? Does the coaching agent handle session-only evaluation?

---

## Execution Notes

- Tasks 1-3 are bundle structural fixes (prerequisites). They can be done in any order.
- Task 4 (coaching agent update) is the most important and most nuanced.
- Task 5 (recipe creation) depends on Task 4 being done (the recipe references the updated agent).
- Task 6 is documentation cleanup — do it last.
- Task 7 is verification — always run it.

Total estimated time: 45-60 minutes for an implementer agent following this plan.
