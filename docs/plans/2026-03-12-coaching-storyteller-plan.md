# Coaching Storyteller Implementation Plan

> **Note:** The agent format in Task 1 was superseded after 5 format iterations during execution. The final shipped format is in `agents/coaching-storyteller.md`.

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a coaching-storyteller agent and 3rd recipe step that transforms the structured coaching evaluation into a narrative coaching letter with scorecard bookend.

**Architecture:** A new `coaching-storyteller` agent receives the structured evaluation from step 2 and produces a hybrid coaching letter (narrative lead → body threads → suggested focus → scorecard table). The recipe gains a 3rd step. The step 2 save path changes from `week-of-` to `eval-` so the evaluation becomes an internal artifact and the coaching letter takes over the user-facing `week-of-` filename.

**Tech Stack:** Agent markdown (YAML frontmatter + prompt), recipe YAML, bundle manifest YAML

**Design doc:** `docs/plans/2026-03-12-coaching-storyteller-design.md`

---

## Task 1: Create the coaching-storyteller agent

Create a new agent file that transforms structured evaluations into narrative coaching letters.

**Files:**
- Create: `agents/coaching-storyteller.md`

**Step 1: Create the agent file**

Create `agents/coaching-storyteller.md` with the following exact content:

```markdown
---
meta:
  name: coaching-storyteller
  description: >
    Transforms a structured coaching evaluation into a narrative coaching letter.
    Produces a hybrid format: narrative lead with the single most important insight,
    body threads that weave dimensions together, a suggested focus in narrative voice,
    and a compact scorecard bookend. Stateless — does not read prior letters. All
    trajectory and delta information flows through the evaluation input.

    <example>
    user: 'Transform this evaluation into a coaching letter'
    assistant: 'I will delegate to builder-coach:coaching-storyteller to produce the coaching letter.'
    <commentary>Evaluation-to-letter transformation triggers the storyteller agent.</commentary>
    </example>
---

# Coaching Storyteller

You transform structured coaching evaluations into coaching letters that create a moment of recognition. You receive a structured evaluation with dimensions, levels, evidence, signal strength, impact moments, a key observation, and a suggested focus. You produce a letter that leads with insight, not structure.

## Output Format

Your letter has exactly four sections, in this order:

### 1. Narrative Lead
Open with the single most important insight — the thing that cuts across dimensions. No preamble, no "here's your evaluation," no greeting. Just the observation, grounded in evidence from the evaluation. This is the sentence that should make the reader stop and think "that's exactly right."

### 2. Body
Develop 2–3 threads from the evaluation. These are NOT one paragraph per dimension. Each thread weaves together dimensions that reinforce each other. Example: a Visibility gap only lands because it contrasts with four Strong dimensions — that's one thread connecting five dimensions, not five sections.

Look for:
- Dimensions that reinforce each other (strengths that compound)
- Tensions between dimensions (a gap that's surprising given other strengths)
- Patterns that only become visible when you stop treating dimensions as separate

### 3. Suggested Focus
One specific, actionable thing. Carry it forward from the evaluation's suggested focus, but reframe it in narrative voice — not a recommendation bullet, but a natural continuation of the letter's argument.

### 4. Scorecard Bookend
A compact markdown table at the end. Three columns: Dimension, Level, Signal. No prose in this section — just the grid. This is the scannable reference that teaches framework vocabulary through repetition across evaluations.

Format:
```
| Dimension | Level | Signal |
|-----------|-------|--------|
| Problem Selection | [level] | [strong/moderate/limited] |
| Leverage Ratio | [level] | [strong/moderate/limited] |
| Taste | [level] | [strong/moderate/limited] |
| Ambition Trajectory | [level] | [strong/moderate/limited] |
| Visibility | [level] | [strong/moderate/limited] |
```

## Writing Constraints

Follow these strictly. They are non-negotiable.

1. **Max 800 words, no padding.** If the insight is sharp and evidence clear, 400 words is fine. Never pad to fill space.
2. **Second person throughout.** "You" not "the builder." This is a letter to a person.
3. **Adaptive tone based on data volume:**
   - Thin data (< 10 sessions) → tentative, curious. Use hedging language: "early patterns suggest," "it looks like," "there are hints of."
   - Moderate data (10–100 sessions) → observational, grounded. State what you see with evidence.
   - Rich data (100+ sessions) → confident, direct. Assert patterns with conviction.
   Read the evaluation's Scope section to determine data volume.
4. **Evidence-first.** Every claim must cite a specific project name, session pattern, metric, or observation from the evaluation. If you can't point to evidence, delete the sentence.
5. **No generic coaching platitudes.** Delete any sentence that could appear in a fortune cookie or a LinkedIn post. "Keep pushing yourself" — delete. "Your journey is unique" — delete. "Growth takes time" — delete. If it's not grounded in THIS evaluation's evidence, it doesn't belong.
6. **No greeting, no sign-off.** Not an email. Starts with the insight, ends with the scorecard table.
7. **No framework jargon in narrative sections.** Dimension names (Problem Selection, Leverage Ratio, Taste, Ambition Trajectory, Visibility) appear ONLY in the scorecard table. In the narrative, describe what you see without naming the framework category.
8. **Stateless.** Do not reference prior coaching letters. Do not say "as I mentioned last time." All trajectory and comparison information is already in the evaluation input — use it as presented.

## Process

1. Read the full evaluation carefully. Identify the Key Observation — this is your narrative lead.
2. Find 2–3 threads where dimensions connect. Don't just restate each dimension.
3. Reframe the Suggested Focus in narrative voice.
4. Build the scorecard table from the dimension assessments.
5. Review your draft: delete any sentence that is generic, jargon-heavy, or unsupported by evidence.
6. Check word count. If over 800, cut the weakest thread.

---

@foundation:context/shared/common-agent-base.md
```

**Step 2: Verify the file was created**

Run: `cat agents/coaching-storyteller.md | head -5`
Expected: Shows the YAML frontmatter opening (`---` and `meta:`)

**Step 3: Commit**

```
git add agents/coaching-storyteller.md
git commit -m "feat(agent): add coaching-storyteller — transforms evaluations into narrative letters"
```

---

## Task 2: Register the agent in bundle.md

Add the new agent to the bundle's agents include list so Amplifier can discover it.

**Files:**
- Modify: `bundle.md` (line 16 area)

**Step 1: Update the agents include list**

In `bundle.md`, find this block (lines 14–16):

```yaml
agents:
  include:
    - builder-coach:coaching-agent
```

Replace it with:

```yaml
agents:
  include:
    - builder-coach:coaching-agent
    - builder-coach:coaching-storyteller
```

**Step 2: Verify the change**

Run: `grep -A 3 "agents:" bundle.md`
Expected output includes both `builder-coach:coaching-agent` and `builder-coach:coaching-storyteller`

**Step 3: Commit**

```
git add bundle.md
git commit -m "feat(bundle): register coaching-storyteller agent"
```

---

## Task 3: Update step 2 save path from `week-of-` to `eval-`

The structured evaluation becomes an internal artifact. Change its save path so the user-facing `week-of-` filename is freed up for the coaching letter.

**Files:**
- Modify: `recipes/session-history-analyzer.yaml` (lines 86–91)

**Step 1: Update the coaching-evaluation step prompt**

In `recipes/session-history-analyzer.yaml`, find the last 5 lines of the file (lines 87–91):

```yaml
      After writing your evaluation, save the report to `{{reports_dir}}/`.
      Use today's date, normalized to Monday of the current week, as the filename:
      `week-of-YYYY-MM-DD.md`.
```

Replace with:

```yaml
      After writing your evaluation, save it to `{{reports_dir}}/`.
      Use today's date, normalized to Monday of the current week, as the filename:
      `eval-YYYY-MM-DD.md`.

      This evaluation is an internal artifact — the coaching letter step will
      produce the user-facing report.
```

**Step 2: Verify the change**

Run: `tail -10 recipes/session-history-analyzer.yaml`
Expected: Shows `eval-YYYY-MM-DD.md` (not `week-of-`)

**Step 3: Commit**

```
git add recipes/session-history-analyzer.yaml
git commit -m "refactor(recipe): change eval save path from week-of- to eval- (now internal artifact)"
```

---

## Task 4: Add the coaching-letter step to the recipe

Add step 3 to the recipe. This step passes the structured evaluation to the storyteller agent, which produces the user-facing coaching letter.

**Files:**
- Modify: `recipes/session-history-analyzer.yaml` (append after the last line)

**Step 1: Append the new step**

Add the following block to the end of `recipes/session-history-analyzer.yaml`, immediately after the coaching-evaluation step (after the line with `eval-YYYY-MM-DD.md`):

```yaml

  # ==========================================================================
  # Step 3: Transform evaluation into user-facing coaching letter
  # ==========================================================================
  - id: coaching-letter
    agent: "builder-coach:coaching-storyteller"
    prompt: |
      Here is the structured coaching evaluation:

      {{coaching-evaluation}}

      Transform this evaluation into a coaching letter. Follow your output format
      and writing constraints exactly.

      After writing the letter, save it to `{{reports_dir}}/`.
      Use today's date, normalized to Monday of the current week, as the filename:
      `week-of-YYYY-MM-DD.md`.
```

**Step 2: Verify recipe structure**

Run: `grep "^  - id:" recipes/session-history-analyzer.yaml`
Expected output (3 steps):
```
  - id: gather-evidence
  - id: coaching-evaluation
  - id: coaching-letter
```

**Step 3: Verify YAML is valid**

Run: `python3 -c "import yaml; yaml.safe_load(open('recipes/session-history-analyzer.yaml')); print('Valid YAML')"`
Expected: `Valid YAML`

**Step 4: Commit**

```
git add recipes/session-history-analyzer.yaml
git commit -m "feat(recipe): add coaching-letter step — storyteller transforms eval into narrative letter"
```

---

## Task 5: End-to-end verification

Run the full 3-step recipe to validate that the pipeline produces both output files with correct structure.

**Step 1: Verify all files are in place**

Run these checks:

```bash
# Agent exists
test -f agents/coaching-storyteller.md && echo "OK: storyteller agent exists"

# Agent is registered in bundle
grep "coaching-storyteller" bundle.md && echo "OK: agent registered in bundle"

# Recipe has 3 steps
STEP_COUNT=$(grep -c "^  - id:" recipes/session-history-analyzer.yaml)
echo "Recipe has $STEP_COUNT steps (expected: 3)"

# Recipe references storyteller agent
grep "coaching-storyteller" recipes/session-history-analyzer.yaml && echo "OK: recipe uses storyteller"

# Recipe step 2 saves to eval- path
grep "eval-YYYY-MM-DD" recipes/session-history-analyzer.yaml && echo "OK: step 2 saves to eval-"

# Recipe step 3 saves to week-of- path
grep "week-of-YYYY-MM-DD" recipes/session-history-analyzer.yaml && echo "OK: step 3 saves to week-of-"
```

Expected: All checks print OK, step count is 3.

**Step 2: Run the recipe end-to-end**

Run:
```
amplifier tool invoke recipes operation=execute recipe_path=@builder-coach:recipes/session-history-analyzer.yaml
```

This will execute all 3 steps sequentially:
1. `gather-evidence` — scans session history
2. `coaching-evaluation` — produces structured eval, saves to `data/reports/eval-YYYY-MM-DD.md`
3. `coaching-letter` — transforms eval into letter, saves to `data/reports/week-of-YYYY-MM-DD.md`

**Step 3: Validate output files**

After the recipe completes, verify both files exist:

```bash
# Check that the evaluation artifact was saved
ls -la data/reports/eval-*.md

# Check that the coaching letter was saved
ls -la data/reports/week-of-*.md
```

**Step 4: Validate coaching letter structure**

Read the generated `data/reports/week-of-YYYY-MM-DD.md` and verify:
- [ ] Starts with an insight (no greeting, no preamble)
- [ ] Body has 2–3 threads weaving dimensions together (not one section per dimension)
- [ ] Suggested focus is present and specific
- [ ] Ends with a scorecard table (Dimension × Level × Signal)
- [ ] No dimension names (Problem Selection, Leverage Ratio, etc.) appear outside the scorecard
- [ ] Second person ("you") throughout
- [ ] Under 800 words
- [ ] No generic platitudes
- [ ] Evidence cites specific projects/patterns from the evaluation

**Step 5: Commit the generated reports**

```
git add data/reports/
git commit -m "chore: add first coaching letter and evaluation artifacts from 3-step pipeline"
```

---

## Execution Notes

- **Tasks 1–4 are all file creation/edits.** No Python code, no pytest. Verification is structural (file exists, YAML parses, grep matches).
- **Task 5 is the real test.** The end-to-end recipe run validates the full pipeline.
- **Task order matters:** Tasks 1–4 can be done in any order, but all must be complete before Task 5.
- **The 336 Python tests are unaffected.** Don't run pytest — these changes are agent prompts and recipe YAML, not Python modules.
- **If the coaching letter quality is poor** on the first run, iterate on the storyteller agent prompt (`agents/coaching-storyteller.md`) — the writing constraints section is the lever.

Total estimated time: 20–30 minutes for an implementer agent following this plan.
