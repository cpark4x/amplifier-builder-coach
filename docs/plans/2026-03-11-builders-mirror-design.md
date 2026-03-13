# Builder's Mirror Design

> **As Built (2026-03-12):** The final implementation diverged from this design: the Writer Agent was replaced by coaching-storyteller, the 4-step chain became 3 steps (no Journal Ingest in the on-demand recipe), and the letter format evolved from conversational prose to the assessment structure defined in `agents/coaching-storyteller.md`.

## Goal

Build an Amplifier bundle called "Builder's Mirror" that helps AI builders develop metacognitive awareness of how they work with AI, so they can become invaluable in the AI future.

## Background

The premise: coding is solved. AI makes building accessible to non-engineers. Traditional PM/engineer/designer roles are dissolving, and what matters now is a new set of skills — problem selection, leverage, taste, ambition, and visibility. But most people have no way to see whether they're actually developing these skills or just staying comfortable.

Builder's Mirror exists because self-awareness is the bottleneck. You can't improve what you can't see. The tool analyzes Amplifier session history combined with self-reported events, evaluates against a growth framework, and produces coaching output — a mirror that shows you your shape as a builder and how that shape is changing over time.

### Inspiration

- **Sam Schillace's Sunday Letters** — system thinking, thinking like a programmer, the idea of a regular written reflection that compounds
- **The "coding is solved" thesis** — AI makes building accessible; what matters now is taste, judgment, and ambition
- **Brian Krabach / Amplifier ecosystem** — the modular AI agent framework this tool is built on and for
- **amplifier-stories community** — what people are actually shipping with AI
- **withamplifier.com** — the platform

## Approach

**Amplifier Bundle** — a bundle + recipe pair native to the Amplifier ecosystem. The user eats their own cooking: building with Amplifier makes them better at the thing the tool coaches on. It's composable, shareable, and buildable today.

This was chosen over alternatives (standalone app, generic LLM wrapper) because it lives where the work happens. The tool observes your Amplifier sessions directly — no export, no copy-paste, no context switching. And because Amplifier bundles are shareable, this can become a community tool.

## Architecture

The bundle (`amplifier-builders-mirror`) contains four components:

```
amplifier-builders-mirror/
├── recipes/
│   ├── weekly-retrospective.yaml   # Core product — weekly coaching pipeline
│   └── session-nudge.yaml          # Thin A — single-line session intention
├── agents/
│   └── coaching-agent.yaml         # Knows the growth framework, evaluates patterns
└── data/
    └── growth-journal.md           # Self-reported events and entries
```

### Flow: Weekly Retrospective

```
Session Analyst ──→ Journal Ingest ──→ Coaching Agent ──→ Writer Agent
(mines logs)       (reads self-      (evaluates against   (produces weekly
                    reported entries)  5 dimensions)        letter + chart)
```

### Flow: Session-Start Nudge

```
Coaching Agent ──→ Single-line intention
(reads latest weekly report + recent sessions)
```

## Components

### The Growth Framework — Five Dimensions + Impact Moments

The framework is role-agnostic. Not "what makes a PM good at AI" but "what makes someone an invaluable AI builder."

#### Five Weekly Dimensions

| Dimension | What It Measures | Observable From |
|-----------|-----------------|-----------------|
| **Problem Selection** | Are you choosing to work on things that matter? Not what's easy — what's important. | What you choose to build, session over session. Is it getting more ambitious, more novel, or staying comfortable? |
| **Leverage Ratio** | How much output per unit of input? Can a 2-sentence prompt produce something substantial? | Iteration count, time-to-result, how much you accomplish per session. Are you getting more leveraged over time? |
| **Taste** | Do you know when something is good? Do you refine or ship the first thing that works? The irreducibly human layer. | Whether you iterate toward quality, go back and improve past work, or just accept first output. |
| **Ambition Trajectory** | Is what you're building getting harder and more interesting over time? | Project complexity over time, scope of what you attempt. Moving from building for yourself to building things that change how others work. |
| **Visibility** | Are you making your thinking and building available to others? | Self-reported entries about publishing, sharing, writing, contributing to communities. |

#### Impact Moments Tracker

Impact is a lagging indicator — someone using your tool might take weeks to happen. So it lives outside the five weekly dimensions as a milestone log:

- Logged when someone uses your tool, gives feedback, or adopts your work
- The coaching agent asks about this during the weekly retrospective
- Celebrated in the weekly letter when it happens
- Noticed when absent: *"You've been building great stuff but nobody knows about it. What's one thing you could share this week?"*

The split: **Visibility** (the leading indicator) tracks the behavior that creates impact. **Impact Moments** (the milestone log) tracks when impact actually lands.

### The Weekly Retrospective Recipe (Core Product)

A chain of four agents:

**1. Session Analyst**
Mines Amplifier session logs from the past week. Extracts:
- What was built
- Tools used
- Iteration counts
- How problems were framed
- What was completed vs. abandoned
- Session duration

**2. Journal Ingest**
Reads the growth journal (self-reported entries). Merges with session data to create a complete picture of the week — both what the tool saw and what it couldn't.

**3. Coaching Agent**
Evaluates combined evidence against the five dimensions. Produces qualitative observations with specific evidence — not numeric scores.

Example output: *"You chose to build X this week. That's more ambitious than last week's Y. But you abandoned it after 2 sessions — what happened?"*

**4. Writer Agent**
Produces the weekly report in two parts:

**Part 1: The Letter**
- What you actually did this week (the facts)
- How you're tracking on each dimension (the mirror)
- One specific thing to try next week (the nudge)
- Your trajectory over time ("this is week 6, here's how you've changed")
- Impact Moments celebration when applicable
- Conversational tone — think Sam Schillace's Sunday Letters but written TO you, ABOUT you

**Part 2: The Growth Chart**
- Radar/spider chart showing five dimensions over time
- Not numeric scores but qualitative levels: low / emerging / developing / strong / exceptional
- Shows your "shape" as a builder
- Key insight: not where you are, but what shape you are. A lopsided builder looks different from a balanced one.

### The Session-Start Nudge

A lightweight recipe run at the top of a session. It reads the most recent weekly report and produces **one single line** — an intention for this session.

Examples:
- *"Last week your leverage ratio was flat. Today, try to accomplish something meaningful in under 3 exchanges with the agent."*
- *"You haven't started anything new in 2 weeks. Today, pick a problem you've never worked on."*
- *"You abandoned your last project after one session. Today, go back and finish it — compounding only works if you complete things."*

What it does NOT do:
- No lengthy briefing
- No multi-paragraph analysis
- No recap of the week

One line. One intention. Then get out of the way and let you work.

### The Growth Journal

How self-reporting works — the input you provide beyond what session logs capture.

**Format:** A simple markdown file (or set of files) in the bundle's data directory.

**Entry methods:**
- During a session: `"Log: published a blog post about multi-agent patterns"`
- Between sessions: edit the journal file directly
- During the weekly retrospective: the coaching agent asks 2-3 quick questions (*"Did you share anything this week? Did anyone use something you built?"*)

**What gets logged:**
- Things published or shared (feeds the Visibility dimension)
- Feedback or adoption signals (feeds Impact Moments)
- Conversations or insights not in session logs (*"talked to Brian Krabach about X"*)
- Intentions or goals (*"this week I want to focus on composition thinking"*)

**What does NOT go here:** Anything already in session logs. The tool handles that automatically.

## Data Flow

```
┌─────────────────────────┐     ┌──────────────────┐
│  Amplifier Session Logs │     │  Growth Journal   │
│  (automatic)            │     │  (self-reported)  │
└───────────┬─────────────┘     └────────┬─────────┘
            │                            │
            ▼                            ▼
     Session Analyst              Journal Ingest
            │                            │
            └──────────┬─────────────────┘
                       │
                       ▼
               Coaching Agent
          (evaluates 5 dimensions)
                       │
                       ▼
                 Writer Agent
                       │
              ┌────────┴────────┐
              ▼                 ▼
        Weekly Letter     Growth Chart
        (qualitative)     (radar shape)
              │                 │
              └────────┬────────┘
                       │
                       ▼
              Weekly Report File
                       │
                       ▼
           Session-Start Nudge
           (reads latest report,
            produces one line)
```

## Error Handling

- **No session logs available:** First-week bootstrap — the coaching agent acknowledges the cold start and focuses on the growth journal and stated intentions. No fake observations.
- **Empty growth journal:** The retrospective still runs on session data alone. The letter gently nudges: *"I can only see what happens in sessions. If you shipped, shared, or learned something outside Amplifier this week, add it to your journal."*
- **Abandoned sessions / incomplete data:** The session analyst flags incomplete sessions without judgment. The coaching agent decides whether it's a pattern worth mentioning.
- **Recipe execution failures:** Standard Amplifier recipe error handling — retry logic, checkpointing for resumability.

## Testing Strategy

- **Coaching Agent quality:** Test with synthetic session logs and journal entries. Verify the agent produces observations grounded in evidence (not generic platitudes) and correctly maps evidence to dimensions.
- **Session Analyst accuracy:** Test extraction against real session logs. Verify iteration counts, completion detection, and timing data are accurate.
- **Writer Agent tone:** Review generated letters for conversational tone, specificity, and actionability. The letter should feel like it was written by someone who watched you work — not a report card.
- **Nudge quality:** Test that nudges are single-line, specific, and derived from the latest report. Reject anything that reads like a paragraph or a generic motivational quote.
- **End-to-end weekly flow:** Run the full retrospective pipeline on a week of real usage data. Verify the output is something you'd actually want to read on a Sunday morning.
- **Growth chart tracking:** Verify qualitative levels change appropriately over multiple weeks and the radar shape reflects actual behavior changes.

## Weekly Time Commitment

5-10 minutes:
- Run the retrospective recipe (~2 min to execute)
- Read the letter (~2 min)
- Glance at growth chart shape (~30 sec)
- Optionally add journal entries for next week (~1-2 min)

## Resolved Design Decisions

_(Originally open questions — resolved 2026-03-11 during dev-machine admissions.)_

- **Journal entry format:** Free-form markdown. Already implemented in `data/growth-journal.md`. Lower friction; the journal parser (spec 002) handles date-header extraction.
- **First-week bootstrap:** Handled by the coaching agent's cold-start instructions: "This is your first week, so I'm establishing your baseline rather than tracking trajectory."
- **Growth chart rendering:** Text-based radar chart. Already defined in the weekly retrospective recipe's writer step. Pure markdown, no image dependencies.
- **Report storage:** One file per week, saved to `data/reports/week-of-[YYYY-MM-DD].md`. Already in the recipe. Easier directory listing for historical comparison.
- **Qualitative level definitions:** Already defined in `context/growth-framework.md` — 2-3 sentence definitions per level per dimension. The coaching agent uses these directly.
