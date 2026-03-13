---
bundle:
  name: builder-coach
  version: 0.1.0
  description: >
    Metacognitive coaching for AI builders. Analyzes Amplifier session history
    against a growth framework to surface patterns, produce on-demand coaching
    insights, weekly retrospective letters, and session-start nudges.

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/microsoft/amplifier-bundle-recipes@main
  - bundle: builder-coach:behaviors/coaching

---

# Builder Coach

**Metacognitive coaching for AI builders — starting from your session data.**

Coding is solved. What matters now is problem selection, leverage, taste, ambition, and visibility. But you can't improve what you can't see. Builder Coach reads your Amplifier session history directly — no manual input required — and reflects your growth back to you: a mirror that shows your shape as a builder and how that shape is changing over time.

## What This Bundle Provides

### Growth Framework
Five dimensions that define what makes someone an invaluable AI builder:
- **Problem Selection** — Are you choosing to work on things that matter?
- **Leverage Ratio** — How much output per unit of input?
- **Taste** — Do you know when something is good?
- **Ambition Trajectory** — Is what you're building getting harder over time?
- **Visibility** — Are you making your thinking available to others?

Plus an **Impact Moments** milestone tracker for when your work lands.

### Automated Workflows (3 Recipes)
- **session-history-analyzer** — Run on-demand. Reads your session history directly and produces a coaching snapshot — no journal input required.
- **weekly-retrospective** — Run weekly. Chains session analysis → journal ingest → coaching evaluation → written report with growth chart.
- **session-nudge** — Run at session start. One line, one intention, based on your latest report.

### Coaching Agent
- **coaching-agent** — Evaluates your sessions against the growth framework. Produces qualitative observations grounded in evidence.

## Quick Start

```
"Analyze my sessions"
"Give me my session nudge"
```

## On-Demand Usage

Run the session history analyzer anytime — no setup, no journal entries needed. Your session data is already there. For a deeper weekly reflection, run the full retrospective recipe.

---

@builder-coach:context/coach-instructions.md

@foundation:context/shared/common-system-base.md
