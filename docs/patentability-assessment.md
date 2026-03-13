# Patentability of AI Developer Tools

## The Short Answer

One of your five tools has a credible path to a patent. The rest don't — but that doesn't mean they're unprotected.

## Tool-by-Tool Verdict

| Tool | Verdict | Why |
|---|---|---|
| **Builder Coach** | **File provisional patent** | Novel category — "meta-cognitive AI usage coaching" from session logs. Limited prior art. Three original elements. |
| **Development Machine** | Consider only if specific mechanisms are novel | C3 AI's US 12,111,859 already covers the general orchestrator-delegates-evaluator pattern. Your angle: persistence, scheduling, or quality evaluation protocols specific to AI coding sessions. |
| **Change Advisor** | Trade secret | CodeRabbit, Qodo, GitHub Copilot for PRs, SonarQube — the field is packed. Your multi-lens framework is valuable IP but not patentable. |
| **Canvas Specialists** | Trade secret | CrewAI, ChatDev 2.0, AutoGen, LangGraph, DSPy all implement researcher→analyzer→writer pipelines. |
| **Session History Analyzer** | Bundle with Builder Coach | The workflow engine is standard. The analytical application is where novelty lives — same novelty as Builder Coach. |

## Why Builder Coach Is the Candidate

Three elements distinguish it from anything in the prior art:

1. **Session log analysis for human development patterns.** Existing tools analyze session data to evaluate code quality or AI performance. Nobody is analyzing how a human *grows as a builder* through their AI usage patterns.

2. **Computational 5-dimension growth framework.** Problem Selection, Leverage Ratio, Taste, Ambition Trajectory, Visibility — applied as a structured, computational assessment lens to session telemetry. No prior art implements this.

3. **The meta-cognitive inversion.** Most AI evaluation tools point inward (is the AI good?). This points outward (is the human getting better at using AI?). That inversion is the core insight and the most defensible element.

## The Alice Problem

Even with novelty, Builder Coach faces a specific legal hurdle. Under the Alice framework, a patent examiner will argue:

- "Coaching a human is a human activity" (Step 2A, Prong 1)
- "Analyzing log files and producing evaluative text is abstract" (Step 2A, Prong 2)

To survive, your claims must anchor to **specific computational methods** — not what the tool does ("evaluates developer growth") but how it does it ("transforms structured session event streams through [specific algorithm] to produce dimensional assessments using [specific data transformation pipeline]").

The July 2024 USPTO guidance makes this harder: "AI" and "neural network" are treated as conventional. The spec must explain how your approach enables improvements that were previously impossible.

**What to document now:**
- The exact data transformation pipeline from events.jsonl → dimensional scores
- Specific algorithms for signal extraction (not "we use an LLM to analyze")
- Data structures for intermediate representations
- Processing efficiency metrics — scale capabilities that distinguish this from manual coaching

## What to Do

1. **This week:** Document the technical methodology of Builder Coach in detail. Algorithms, data transformations, processing stages. Not what it does — how it computes.

2. **Within 30 days:** File a provisional patent application ($2K–$5K with attorney). This establishes your priority date while you refine claims.

3. **Immediately:** Consult a patent attorney who specializes in software/AI patents and has experience navigating §101 rejections. Show them Builder Coach specifically.

4. **For everything else:** Implement trade secret protections — access controls, documentation of proprietary methods, NDAs where relevant. Your prompts, evaluation criteria, dimensional frameworks, and pipeline configurations are valuable. They're just better protected as secrets than as patents.

## The Honest Bottom Line

Market novelty ≠ patent novelty. You've built tools that are commercially innovative and technically impressive. But patent law asks a narrower question: does the *technical implementation* involve an inventive concept beyond applying conventional computing to a new domain?

For Builder Coach, the answer is probably yes — if the claims are drafted around the computational method, not the coaching concept. For the rest, the answer is probably no, and that's fine. Trade secrets protect what patents can't.

---

*This is research-based analysis, not legal advice. Patent eligibility depends on specific claim language and jurisdiction. Consult a qualified patent attorney.*
