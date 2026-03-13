# Builder Coach Constitution

The authoritative reference for all development on amplifier-builder-coach.
Read this before building any feature. When in doubt, this document wins.

---

## What This Is

A metacognitive coaching bundle for AI builders. It analyzes Amplifier session
history and self-reported journal entries against a growth framework, producing
weekly coaching letters and session-start nudges.

The user eats their own cooking — building with Amplifier makes them better at
what the tool coaches on.

## Architecture

### The Pipeline

Two workflows, one core pipeline:

**Weekly Retrospective** (the core product):
```
Session Analyst → Journal Ingest → Coaching Agent → Writer Agent
```

**Session-Start Nudge** (lightweight):
```
Coaching Agent → single-line intention
```

### Component Map

```
amplifier-builder-coach/
├── bundle.md                           # Bundle declaration
├── context/
│   └── growth-framework.md             # The 5-dimension framework (source of truth)
├── agents/
│   └── coaching-agent.md               # Evaluates against the framework
├── recipes/
│   ├── weekly-retrospective.yaml       # 4-step coaching pipeline
│   └── session-nudge.yaml              # Single-line intention generator
├── data/
│   ├── growth-journal.md               # User's self-reported entries
│   └── reports/                        # Weekly report output (one file per week)
├── src/
│   └── builder_coach/                  # Python utility modules
│       ├── __init__.py
│       ├── session_discovery.py        # Find session files by date
│       ├── journal_parser.py           # Parse journal markdown into entries
│       └── growth_chart.py             # Render text-based growth charts
├── specs/                              # Feature specifications
├── tests/                              # All tests (pytest)
└── docs/
    ├── CONSTITUTION.md                 # This file
    └── plans/                          # Historical design documents
```

### Module Boundaries

| Module | Responsibility | Inputs | Outputs |
|--------|---------------|--------|---------|
| `session_discovery` | Find and filter session files | Search paths, day range | List of `SessionFile` |
| `journal_parser` | Parse journal markdown | Journal file path | List of `JournalEntry` |
| `growth_chart` | Render text growth charts | `BuilderShape` | Markdown string |
| `coaching-agent` | Evaluate against growth framework | Session data + journal data | Structured evaluation |
| `weekly-retrospective` | Orchestrate the 4-step pipeline | Context variables | Weekly report file |
| `session-nudge` | Generate session intention | Latest report | Single line |

Modules do NOT reach into each other. Data flows through the pipeline via
recipe context accumulation, not direct imports between modules.

## Data Model

### SessionFile

```python
@dataclass
class SessionFile:
    path: Path
    session_id: str       # directory name
    modified: datetime     # events.jsonl mtime
    size_bytes: int
```

### JournalEntry

```python
@dataclass
class JournalEntry:
    date: date
    raw_text: str          # full text under the date header
    tags: list[str]        # extracted #hashtags
```

### Level (qualitative growth levels)

```python
class Level(Enum):
    LOW = "Low"
    EMERGING = "Emerging"
    DEVELOPING = "Developing"
    STRONG = "Strong"
    EXCEPTIONAL = "Exceptional"
```

These are the ONLY valid levels. Never use numeric scores. Never invent
intermediate levels. The coaching agent assigns levels using the definitions
in `context/growth-framework.md`.

### BuilderShape

```python
@dataclass
class DimensionScore:
    name: str
    current: Level
    previous: Level | None = None  # None on cold start

@dataclass
class BuilderShape:
    problem_selection: DimensionScore
    leverage_ratio: DimensionScore
    taste: DimensionScore
    ambition_trajectory: DimensionScore
    visibility: DimensionScore
```

### Coaching Evaluation Output

The coaching agent produces structured markdown consumed by the writer:

```
## Coaching Evaluation — [DATE]

### This Week's Evidence
[Brief summary]

### Dimension Assessments
**Problem Selection: [Level]**
[2-3 sentences with specific evidence]
... (repeat for all 5 dimensions)

### Impact Moments
[Events or their absence]

### Key Observation
[One cross-dimension insight]

### Suggested Focus
[One specific, actionable thing]
```

### Weekly Report Output

Saved to `data/reports/week-of-YYYY-MM-DD.md` (Monday date). Assessment format:

```
### Your snapshot
2-4 sentences. Am I doing well or not?

### What's working
2-3 bold items with 1-2 evidence sentences each

### What to reconsider
1-2 bold items (deduplicated — never restate the same gap)

### What to try next
One specific, actionable thing

---
| Dimension | Level | Signal |
|-----------|-------|--------|
| Problem Selection | [level] | [short phrase] |
| Leverage Ratio | [level] | [short phrase] |
| Taste | [level] | [short phrase] |
| Ambition Trajectory | [level] | [short phrase] |
| Visibility | [level] | [short phrase] |
```

300 word max (scorecard extra). Second person. Adaptive tone (thin < 10 sessions = tentative; moderate 10–100 = observational; rich 100+ = confident). No framework jargon outside scorecard. No Amplifier tool names.

## Technology Choices

| Choice | Decision | Rationale |
|--------|----------|-----------|
| Language | Python 3.11+ | Amplifier ecosystem language |
| Package manager | uv | Fast, handles venvs automatically |
| Test framework | pytest | Standard, fast, 0.08s current suite |
| Linter | ruff | Formatting + linting in one tool |
| Bundle format | Amplifier bundle (markdown + YAML) | Native to the ecosystem |
| Journal format | Free-form markdown with `## YYYY-MM-DD` date headers | Low friction, parseable |
| Report storage | One markdown file per week | Simple directory listing for history |
| Growth chart | Text-based radar in markdown | No image dependencies |

## Conventions

### File Naming

- Python modules: `snake_case.py` in `src/builder_coach/`
- Tests: `test_<module>.py` in `tests/`
- Specs: `NNN-<feature-name>.md` in `specs/`
- Reports: `week-of-YYYY-MM-DD.md` in `data/reports/`

### Code Style

- ruff format + ruff lint (configured in `pyproject.toml`)
- Line length: 100
- Type hints on function signatures
- Dataclasses for data structures (not dicts)
- Standard library only unless a dependency is explicitly justified

### Testing

- Every Python module has a corresponding test file
- Tests are behavioral (verify what the function does, not implementation details)
- Edge cases from the spec get their own test functions
- Test names describe the scenario: `test_discover_sessions_skips_missing_directories`
- Run: `uv run pytest tests/ -v`
- Lint: `uv run ruff check .`

### Agent Instructions

- Observations must cite specific evidence (sessions, journal entries, patterns)
- Use qualitative levels only (Low/Emerging/Developing/Strong/Exceptional)
- Never generate generic advice ("keep pushing yourself" = failure)
- Cold start is acknowledged explicitly, never faked

## The Five Dimensions (Reference)

Defined in full at `context/growth-framework.md`. Summary:

| Dimension | Measures | Primary Signal |
|-----------|----------|----------------|
| Problem Selection | Quality of problems chosen | Session logs (what was built) |
| Leverage Ratio | Output per unit of input | Session logs (iteration count, efficiency) |
| Taste | Ability to judge and refine quality | Session logs (iteration toward quality) |
| Ambition Trajectory | Complexity growth over time | Session logs (project scope trend) |
| Visibility | Making work available to others | Journal entries (sharing, publishing) |

Plus **Impact Moments** — a lagging indicator milestone log tracked via journal.

## Design Decisions Log

| Date | Decision | Context |
|------|----------|---------|
| 2026-03-11 | Free-form markdown for journal | Lower friction, already implemented |
| 2026-03-11 | Text-based growth chart | Already defined in recipe, no image deps |
| 2026-03-11 | One report file per week | Already in recipe save path, simpler history |
| 2026-03-11 | Cold start handled in coaching agent | Explicit baseline framing, no fake history |
| 2026-03-11 | Level definitions in growth framework | 2-3 sentence definitions per level per dimension |
| 2026-03-12 | Added coaching-storyteller agent | Dedicated agent transforms structured eval into user-facing coaching letter; replaces generic writer agent |
| 2026-03-12 | Assessment format (not narrative prose) | 5-iteration UX refinement: narrative arc was slower to scan; assessment format (snapshot → working → reconsider → try next → scorecard) gives sharper signal |

## Rules for the Machine

1. **Read this document before starting any feature.**
2. **Check the spec** in `specs/` for the feature you're building.
3. **Write the test first.** Watch it fail. Then implement.
4. **Standard library only** unless the spec explicitly allows a dependency.
5. **One module, one responsibility.** Don't add session logic to the journal parser.
6. **Run `uv run pytest tests/ -v` and `uv run ruff check .`** before claiming done.
7. **Don't modify the growth framework** without explicit instruction. It's the source of truth.
8. **Don't modify the coaching agent's output format** — the coaching-storyteller agent depends on it.
9. **Qualitative levels only.** Never introduce numeric scores anywhere.
10. **When in doubt, do less.** A smaller correct feature beats a larger wrong one.