# Session History Analyzer Design

## Goal

Build an on-demand session history analyzer that produces a structured coaching evaluation across all five growth dimensions purely from Amplifier session data, with no user input required.

## Background

The amplifier-builder-coach bundle is a metacognitive coaching system for AI builders. It evaluates growth across five dimensions — Problem Selection, Leverage Ratio, Taste, Ambition Trajectory, and Visibility — plus Impact Moments. The project already has a solid preprocessing layer: 8 Python utility modules with 318 passing tests that handle session discovery, extraction, evidence combination, and report management.

The critical product insight driving this design is that most users — conservatively more than two-thirds — will never write journal entries. The system must deliver its full coaching value from session data alone. Journal entries become an optional enhancement later, once users have experienced the system driving value consistently from what it can already observe. This is validated by competitive research: Claude Code's `/insights` command demonstrates that real value can be delivered with zero user input.

The Session History Analyzer is the component that closes the loop — it takes the raw preprocessing output and turns it into actionable coaching feedback.

## Approach

A single Amplifier recipe with two steps: a Python preprocessing step that gathers and structures all available evidence, followed by a coaching agent step that evaluates the evidence and writes the report.

This was chosen over alternatives (separate tool module, multi-recipe pipeline) for simplicity. The preprocessing step is generous — it hands over everything it finds, summarizing but never filtering. The coaching agent receives the full picture and makes all evaluative decisions. This clean separation means the preprocessor stays deterministic and testable while the agent handles the nuanced judgment work.

The system is invoked on-demand rather than on a weekly cadence. Users run it whenever they want:

```bash
amplifier run --bundle ~/Projects/amplifier-builder-coach "analyze my sessions"
```

Or after publishing:

```bash
amplifier run --bundle git+https://github.com/user/amplifier-builder-coach@main "analyze my sessions"
```

### Differentiators vs. Claude Code `/insights`

The `/insights` command provides a useful snapshot, but this system goes further in three specific ways:

1. **Longitudinal growth tracking.** Rather than a point-in-time summary, the analyzer tracks trajectory over time. Each report builds on the last, creating a growth narrative.
2. **Structured 5-dimension coaching model.** Evaluations follow a coherent framework for builder growth, not ad-hoc observations. Users develop a mental model of where they're strong and where they're developing.
3. **Cross-session pattern recognition over weeks and months.** The system can surface insights like "your problem selection has gotten more ambitious over the last 6 weeks" — patterns that are invisible within any single session.

## Architecture

The analyzer follows a two-step pipeline within a single Amplifier recipe.

```
User: "analyze my sessions"
         │
         ▼
┌─ Step 1: Python Preprocessing ──────────────────────────┐
│  discover_sessions(all paths, no time filter)            │
│       → extract_sessions(all found)                      │
│       → combine_evidence(sessions, journal=[], today)    │
│       → format_evidence_markdown(evidence)               │
│                                                          │
│  load_history(reports_dir) → trend data                  │
│  latest_report(reports_dir) → "new vs established"       │
└──────────────────────────────────────────────────────────┘
         │ structured evidence + history context
         ▼
┌─ Step 2: Coaching Agent ────────────────────────────────┐
│  Receives: evidence markdown, last report, trends,       │
│            growth framework                              │
│  Evaluates: all 5 dimensions from session data           │
│  Calibrates: confidence to signal available              │
│  Outputs: coaching report → save_report()                │
└──────────────────────────────────────────────────────────┘
```

The preprocessor is deterministic, tested Python code. The coaching agent is an LLM-driven evaluator with access to the growth framework. The boundary between them is a structured evidence markdown block — a contract that keeps each side independently testable.

## Components

### Step 1: Python Preprocessor

The preprocessor calls the existing Python utility modules in sequence to gather and structure all available session data. It uses six functions from the existing codebase:

**`discover_sessions()`** scans all configured session paths with no time filter applied. The preprocessor is deliberately generous — it finds everything available and lets the agent decide what matters.

**`extract_sessions()`** parses the `events.jsonl` file for each discovered session, producing structured summaries of what happened: tools used, files touched, patterns of work, iteration counts, and session outcomes.

**`combine_evidence()`** merges session summaries into a unified evidence structure. The `journal` parameter is passed as an empty list for now. This is the designed extension point for when journal support is added later — no architectural changes needed, just a non-empty list.

**`format_evidence_markdown()`** renders the combined evidence into an agent-ready markdown block. This is the contract format between preprocessing and the coaching agent.

**`load_history()`** retrieves historical trend snapshots from prior coaching reports, giving the agent longitudinal context for trajectory evaluation.

**`latest_report()`** finds the most recent coaching report, which establishes the boundary between "new evidence" and "established baseline."

### Step 2: Coaching Agent

The coaching agent receives the structured evidence block, the history context, and the growth framework. It performs four jobs:

**Scope determination.** If a prior report exists, everything since that report is "new evidence" and everything before is "established baseline." The agent evaluates the delta. If no prior report exists (first run), everything available becomes the baseline, and the agent frames its output accordingly with appropriate confidence hedging on thin data.

**Dimension evaluation.** The agent evaluates all five growth dimensions from the session data:

- **Problem Selection** — assessed from what users chose to build, the ambition level of their projects, and how they scoped work.
- **Leverage Ratio** — assessed from tool usage patterns, iteration counts, and output produced per session. High leverage means more result per unit of effort.
- **Taste** — assessed from refactoring behavior, revisiting and polishing work versus shipping first passes, attention to edge cases and code quality.
- **Ambition Trajectory** — assessed from the complexity trend over time across sessions. Is the user tackling progressively harder problems?
- **Visibility** — inferred from session activities that indicate sharing behavior: blog post drafts, public repository work, README writing, documentation creation, talk preparation. The agent notices these signals in what users already did, without requiring explicit input.

**Confidence calibration.** The agent is transparent about signal strength per dimension. Some dimensions will have strong signal (Leverage Ratio from tool usage is usually rich), while others may have thin data (Visibility signals may be sparse). The agent evaluates honestly — it does not refuse to assess a dimension due to limited data, but it communicates its confidence level clearly.

**Report generation.** The agent writes the coaching report and saves it via `save_report()`. The report becomes the "latest report" for the next invocation, establishing the new baseline boundary.

### Coaching Agent Updates

The existing coaching agent requires several updates to support this flow:

- **On-demand framing.** Language shifts from "this week" to scope-aware framing like "Analyzing 12 sessions spanning March 1–12."
- **All 5 dimensions from session data.** The agent must evaluate every dimension including Visibility (inferred), not just the subset with strongest signal.
- **Scope and signal transparency.** The agent states what it analyzed and how much data it had, so users understand the basis for each evaluation.
- **Data volume calibration.** The agent adapts its tone and confidence whether it sees 2 sessions or 50.

## Data Flow

The data flow is linear and stateless within a single invocation.

The user triggers the analyzer with a natural language request. The recipe dispatches Step 1, which calls into the Python modules sequentially. Session discovery finds all available session directories. Extraction parses each one into structured summaries. Combination merges them with an empty journal list. Formatting renders the evidence markdown. In parallel, history loading and latest-report lookup provide the longitudinal context.

Step 2 receives all of this as its input context. The coaching agent reads the evidence, determines scope (delta vs. baseline), evaluates each dimension, calibrates confidence, and writes the report. The saved report becomes the anchor point for the next invocation.

There is no feedback loop within a single run. The system is purely analytical: gather, evaluate, report.

## Bundle Structural Fixes

Four prerequisites must be resolved before the analyzer recipe can execute:

**Add recipes bundle to includes.** Without `amplifier-bundle-recipes` in the `includes:` section of `bundle.md`, recipes cannot execute. This is a one-line addition but blocks everything.

**Create `context/coach-instructions.md`.** The coaching agent needs recipe awareness context — a file that tells it what recipes exist and their invocation paths. Without this, the agent cannot be dispatched by the recipe system.

**Fix double-load of `growth-framework.md`.** The growth framework is currently loaded via both `context.include` in YAML and an `@mention` in the markdown body. This causes redundant context consumption. The fix is to drop the `context.include` entry and keep only the `@mention`, which gives the agent more control over when the framework is referenced.

**Verify agent references in recipes.** The existing recipes reference `foundation:story-researcher` and `foundation:technical-writer`, which may not exist in the foundation bundle. These need to be verified and replaced if they point to nonexistent agents.

## Python Module Invocation Strategy

The initial approach is agent-driven: the recipe steps use filesystem and bash tools to call into the Python modules, rather than registering them as a formal Amplifier tool module. The 8 Python modules serve as tested, proven logic that the agent orchestrates.

Promotion to a proper Amplifier tool module (following the foundation bundle's tool registration pattern) happens only if the agent-driven approach proves too slow or imprecise in practice. This avoids premature optimization of the integration layer while the coaching workflow is still being validated.

## Testing Strategy

The preprocessing layer is already well-tested with 318 passing tests across the 8 Python modules. Testing for the new components focuses on:

- **Recipe integration testing.** Verify the recipe executes end-to-end: preprocessing gathers evidence, the agent receives it, and a report is saved. This validates the contract between steps.
- **Scoping logic testing.** Verify correct behavior for both paths: first-run (no prior report, everything is baseline) and subsequent-run (delta from last report).
- **Agent output validation.** Verify the coaching agent addresses all 5 dimensions, includes confidence signals, and adapts framing to the data volume and scope.
- **Bundle structural verification.** Confirm the four prerequisite fixes resolve cleanly — recipes execute, context loads without duplication, and agent references are valid.

## Open Questions

- **Session volume thresholds.** At what point does the evidence block become too large for the agent's context window? May need summarization or windowing for users with hundreds of sessions.
- **Report format evolution.** As longitudinal data accumulates, should the report format evolve to emphasize trends more heavily? The first few reports will naturally be more snapshot-oriented.
- **Journal integration timing.** When journal support is added, how should the agent weight journal evidence vs. session evidence? The architecture supports it (just pass a non-empty list to `combine_evidence`), but the coaching calibration needs thought.
