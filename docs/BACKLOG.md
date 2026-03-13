# Builder Coach Backlog

## Immediate Next

### Builder Coach patentability next steps
Per `docs/patentability-assessment.md`:
- Document the technical methodology (algorithms, data transformations, processing stages)
- Consult a patent attorney specializing in software/AI patents
- Consider provisional patent filing ($2K-$5K)

---

## Done (This Sprint)

- **Adaptive evidence window** — Recipe now defaults to 7-day window, auto-expands (14d → 28d → 90d) if fewer than 5 sessions found. Supports `date_range` override. Closes the scalability timeout issue — no longer tries to scan all 5,554 sessions.
- **Fixed recipe invocation bug** — Added catch-all rule, "coach me" trigger phrase, explicit "do not delegate directly" warning; fixed `@builder-coach:` namespace paths that don't resolve at runtime to relative `recipes/` paths; replaced competing delegation examples in coaching-agent.md with recipe invocation examples
- **Completed this-week evaluation** — Ran steps 2-3 against 5,554-session evidence; produced delta evaluation (eval-2026-03-10.md) and coaching letter (week-of-2026-03-12.md)
- **Ran 7-day scoped evaluation** — 170 sessions across 10 projects; evidence gathering completed in ~2 min (vs 600s timeout with full history)
- **Validated thin-data scenario** — Synthetic 5-session test passed: 8 instances of tentative language, zero confident assertions, "Too early" level for insufficient signal, 232 words (under 300 ceiling)
- **Updated design docs** — Synced 4 files (coaching-storyteller-design, CONSTITUTION, coaching-storyteller-plan, builders-mirror-design) to reflect final assessment format after 5 iterations
- Designed and built coaching-storyteller agent (3rd recipe step)
- Iterated output format through 5 versions → landed on assessment format
- Ran first real end-to-end evaluation (5,554 sessions, 85 days)
- Added timeouts to recipe steps 2 and 3
- Updated coach-instructions.md with explicit recipe invocation
- Completed patentability assessment — Builder Coach identified as strongest candidate
- Saved first coaching letter to data/reports/week-of-2026-03-10.md
