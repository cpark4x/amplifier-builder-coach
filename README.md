# Builder Coach

Metacognitive coaching for AI builders. Builder Coach reads your Amplifier session history, evaluates it against a growth framework, and produces a coaching letter -- no manual input required. It tells you what you're doing well, what to reconsider, and what to try next, grounded in specific evidence from your actual sessions.

## The Growth Framework

Five dimensions define what makes someone an invaluable AI builder:

- **Problem Selection** -- Are you choosing to work on things that matter, or staying comfortable?
- **Leverage Ratio** -- How much output per unit of input? Are you getting better at directing AI?
- **Taste** -- Do you know when something is good? Do you refine, or accept the first thing that works?
- **Ambition Trajectory** -- Is what you're building getting harder over time?
- **Visibility** -- Are you making your thinking available to others?

Plus **Impact Moments** -- a milestone tracker for when your work actually lands (someone uses your tool, adopts your pattern, gives meaningful feedback). Impact is a lagging indicator; Visibility is the leading one.

## Quick Start

Say "Coach me" or "Analyze my sessions" to trigger the full pipeline. No setup required -- your session data is already there.

### Three recipes

| Recipe | Trigger | What it does |
|---|---|---|
| `session-history-analyzer` | "Coach me", "How am I doing" | On-demand. Reads session history, evaluates against the framework, writes a coaching letter. |
| `weekly-retrospective` | "Run the weekly retro" | Full pipeline with journal integration. Session analysis + journal ingest + evaluation + report. |
| `session-nudge` | "Give me my nudge" | Quick. One line, one intention for your current session, based on your latest report. |

### Adaptive evidence window

The session history analyzer defaults to a 7-day window. If fewer than 5 sessions are found, it automatically expands: 7 -> 14 -> 28 -> 90 days. You can override with a specific date range:

```
"Analyze my sessions from the last 30 days"
```

## What You Get

The coaching letter follows a fixed structure:

1. **Snapshot** -- Where you are right now, in one paragraph.
2. **What's working** -- Specific strengths, cited with evidence from your sessions.
3. **What to reconsider** -- Gaps or patterns worth examining. Direct, not harsh.
4. **What to try next** -- Concrete, actionable suggestions tied to specific dimensions.
5. **Scorecard** -- Qualitative levels (Low / Emerging / Developing / Strong / Exceptional) per dimension. No numeric scores.

The tone adapts to data volume. With thin data (few sessions, no journal), the letter is tentative and transparent about signal strength. With rich data, it's confident and specific. It never fabricates observations to fill gaps.

## Architecture

Builder Coach is a 3-step pipeline:

1. **Gather evidence** -- Reads session history (and optionally journal entries) within the evidence window. Structures raw data into per-dimension observations.
2. **Evaluate** -- The `coaching-agent` maps evidence to the five dimensions, assigns qualitative levels, and identifies trajectory changes. Every claim must cite a specific session or pattern.
3. **Write letter** -- The `coaching-storyteller` transforms the structured evaluation into a scannable coaching letter. Stateless -- it doesn't read prior letters.

The agents are recipe steps, not standalone. They expect structured input from the previous pipeline stage. Coaching requests always go through the recipe pipeline.

## Composing Into Your Bundle

The coaching capability is packaged as a composable behavior. To add coaching to another bundle, include it in your `bundle.md`:

```yaml
---
bundle:
  name: my-bundle
  version: 0.1.0

includes:
  - bundle: builder-coach:behaviors/coaching
---
```

This pulls in the coaching agents (`coaching-agent`, `coaching-storyteller`) and the workflow instructions. Your bundle's users can then say "Coach me" and get the full pipeline.

The behavior definition lives at `behaviors/coaching.yaml`:

```yaml
bundle:
  name: coaching-behavior
  version: 0.1.0
  description: >
    Metacognitive coaching capability for AI builders. Compose onto
    any bundle to add builder coaching capability.

agents:
  include:
    - builder-coach:coaching-agent
    - builder-coach:coaching-storyteller

context:
  include:
    - builder-coach:context/coach-instructions.md
```

## License

MIT
