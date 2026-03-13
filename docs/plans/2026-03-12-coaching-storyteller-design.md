# Coaching Letter Storyteller Design

## Goal

Add a coaching-storyteller agent and 3rd recipe step to transform the structured coaching evaluation into a coaching letter that creates a moment of recognition, not just a list of assessments.

## Background

The `session-history-analyzer` recipe currently has two steps: evidence gathering and coaching evaluation against a 5-dimension growth framework (Problem Selection, Leverage Ratio, Taste, Ambition Trajectory, Visibility). The evaluation output is rigorous and evidence-grounded but reads like a report card — five sequential dimension assessments with the best insight buried at the bottom. Real users skim it and feel assessed but not moved.

The core problem is structural: the framework IS the organizer, so every report walks through the same five sections in sequence, distributing attention evenly regardless of where the real signal is. A builder who is Strong across four dimensions and Emerging on one gets equal airtime for all five, burying the actual story.

## Approach

Add a dedicated `coaching-storyteller` agent rather than using the storyteller specialist. The coaching letter has very specific requirements — hybrid structure, framework-as-bookend, adaptive tone, word limit — that would require working around storyteller specialist conventions (StoryOutput format, story-formatter pipeline) rather than working with them. A purpose-built agent keeps the prompt focused and the output predictable.

## Architecture

### Recipe Flow (3 steps)

```
Step 1: gather-evidence
  Agent: foundation:explorer
  Action: Scans Amplifier session history, produces structured evidence
  Status: Unchanged

Step 2: coaching-evaluation
  Agent: builder-coach:coaching-agent
  Action: Evaluates evidence against growth framework
  Output: data/reports/eval-YYYY-MM-DD.md (internal artifact)
  Status: Save path changes from week-of- to eval-; output becomes internal

Step 3: coaching-letter (NEW)
  Agent: builder-coach:coaching-storyteller
  Action: Transforms evaluation into user-facing coaching letter
  Output: data/reports/week-of-YYYY-MM-DD.md (user-facing)
```

### File Outputs

| File | Purpose | Audience |
|------|---------|----------|
| `data/reports/eval-YYYY-MM-DD.md` | Structured evaluation | Internal reference, future delta detection |
| `data/reports/week-of-YYYY-MM-DD.md` | Coaching letter | User-facing |

## Components

### New Agent: `agents/coaching-storyteller.md`

**Input:** The structured coaching evaluation from step 2 — dimensions, levels, evidence, signal strength, impact moments, key observation, suggested focus.

**Output:** A coaching assessment in five sections:

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

**Stateless:** Does not read prior coaching letters. Relies on delta information already present in the evaluation input (the coaching agent already handles "since last report" comparisons).

### Writing Constraints (baked into prompt)

- **300 word max** (scorecard table is extra, not counted). If the insight is sharp and the evidence is clear, shorter is fine.
- **Second person throughout.** "You" not "the builder."
- **Adaptive tone based on data volume:**
  - Thin data (< 10 sessions) → tentative, curious. Hedging language: "early patterns suggest," "it looks like."
  - Moderate data (10–100 sessions) → observational, grounded. State what you see with evidence.
  - Rich data (100+ sessions) → confident, direct. Assert patterns with conviction.
- **Evidence-first.** Every claim cites a specific project, session pattern, or metric from the evaluation. No generic coaching platitudes.
- **No framework jargon outside scorecard.** Dimension names appear only in the scorecard table.
- **No Amplifier tool names.** Never reference Amplifier, bundle names, or internal tooling in the letter.

## Data Flow

```
Session History
  │
  ▼
[gather-evidence] ── explorer scans sessions ──► Structured Evidence
  │
  ▼
[coaching-evaluation] ── coaching agent evaluates ──► eval-YYYY-MM-DD.md
  │                                                    (dimensions, levels,
  │                                                     evidence, signal,
  ▼                                                     impact moments,
                                                        key observation,
[coaching-letter] ── storyteller transforms ──►         suggested focus)
                                               week-of-YYYY-MM-DD.md
                                               (narrative + scorecard)
```

The storyteller receives the full structured evaluation as input context. It does not access session history directly or read prior coaching letters. All trajectory and delta information flows through the evaluation.

## Error Handling

- **Thin evaluation input:** If the coaching evaluation has sparse evidence across dimensions, the storyteller adapts tone to tentative/curious rather than making confident claims. The word count naturally compresses — no padding to fill 800 words.
- **Missing dimensions:** If the evaluation omits a dimension (insufficient data), the scorecard reflects this and the narrative does not fabricate coverage.
- **Step 2 failure:** If the coaching evaluation step fails, step 3 does not execute (standard recipe sequential behavior). The prior `week-of-` report remains as the latest user-facing output.

## Testing Strategy

- **Agent prompt review:** Verify the storyteller prompt encodes all writing constraints (word limit, tone adaptation, evidence-first, no jargon in narrative, scorecard structure).
- **Recipe integration:** Run the 3-step recipe end-to-end and verify both output files are produced at the correct paths.
- **Output structure validation:** Confirm the coaching letter contains all four sections (narrative lead, body threads, suggested focus, scorecard table).
- **Constraint compliance:** Check that output respects word limit, uses second person, omits greetings/sign-offs, and restricts dimension names to the scorecard.
- **Existing tests unaffected:** The 336 passing Python utility tests remain green — this change adds an agent prompt and a recipe step, not Python code.

## What Doesn't Change

- The coaching agent prompt (step 2) — still produces the same structured evaluation
- The evidence gathering step (step 1) — still scans sessions the same way
- The growth framework (`context/growth-framework.md`)
- The Python utility modules (336 tests passing)
- The bundle manifest (`bundle.md`) — already declares the agents include pattern

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Dedicated agent vs. storyteller specialist | Dedicated agent | Coaching letter has specific requirements (hybrid structure, framework-as-bookend, adaptive tone, word limit) that would need to work around specialist conventions rather than with them |
| Output format | Hybrid (narrative + scorecard) | Pure narrative loses scannability. Pure structured report (current state) loses emotional impact. Hybrid gives both. |
| Framework placement | Bookend, not organizer | Current report's problem is that the framework IS the structure, making it repetitive. Narrative leads with insights; scorecard teaches framework vocabulary through repetition across evaluations. |
| Word limit | 800 max, no padding | Respects attention. Current ~900 word report feels long because of even distribution, not actual length. Better allocation makes the same budget feel shorter. |
| State management | Stateless storyteller | Simpler architecture. Coaching agent already handles delta detection, so storyteller naturally gets trajectory information in its input. Can add prior-letter awareness later if output feels disconnected. |
| File outputs | Both eval and letter saved | Structured eval is useful for coaching agent on future runs (delta detection) and for power users who want raw dimension assessments. |
| Narrative lead → Assessment format | 5-iteration UX refinement | Narrative arc was slower to scan; assessment format gives sharper signal. |

## Open Questions

None — design is validated and ready for implementation.
