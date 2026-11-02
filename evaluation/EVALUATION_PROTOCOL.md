# Part 5 — Golden Set evaluation protocol

## What the Golden Set is

The **original 20-record Golden Set** was hand-reviewed and adjudicated for the research Discovery Engine (90% original AI-vs-human theme-label agreement, 18/20). It contains *public conversation observations*, **not** questions with validated answers about Groww product functions. The original 90% must **not** be reused as the quality score of this new MVP.

For the MVP, `golden_set_20_scenarios.json` maps **each original record ID** to a realistic test question, its adjudicated theme, the expected behaviour (source-backed explanation or safe refusal), and acceptable official help source IDs. Test questions are illustrative reconstructions derived from the source observations, **not transcripts or evidence of real user queries**.

## Quality gate (at runtime, visible to users)

1. **Pre-model policy:** reject requests for investment advice or transaction execution, account-specific assertions, other platforms, credentials and unsupported topics.
2. **Approved retrieval:** use at most three manually reviewed Groww help summaries with permanent URLs. No relevant approved source = safe refusal, no model call.
3. **AI inference:** Groq `openai/gpt-oss-20b` summarises the user question and retrieved help extracts, returning structured JSON.
4. **Post-model checks:** required schema, cited source IDs restricted to the provided documents, length checks, refusal of certain unsafe claims/financial pressure or external contact links.
5. **Fail closed:** if model output fails a rule or API times out, show a curated official-source fallback instead, with a **visible gate explanation**.

**Caveat:** The gate checks observable patterns and source identifiers; it cannot establish complete semantic factual correctness, and the retrieval set is limited. Human review is required.

## What has actually been measured

Run from project root:

```bash
python evaluation/run_eval.py
```

**Automated offline regression, 2 Nov 2026:**

- Golden Set-derived cases: **20** (all mapped to original adjudicated IDs and source URLs).
- Automatic route, source-ID alignment and basic safety outcome: **20/20 pass (100%)**.
- In-scope cases eligible for generative AI: **8**; out-of-scope/safety cases: **12**.
- AI answers accepted by the gate: **0/8** because **AI was intentionally disabled in this run**.
- Model factual accuracy: **not measured**.
- Live AI model accuracy: **not measured**.
- Number of real usability participants: **not measured**.

**Development detail:** First implementation scored 17/20; three misses (missing holdings, restricted scheme subscriptions, specific fund advice phrasing) were corrected and retested. The 20-case fixture was derived from the final human-adjudicated CSV. This is a small non-representative developer regression set, and fixes were made after seeing the cases; it is **not** a blind holdout test or evidence of generalisation.

## Required live evaluation for assignment

Once a **real** `GROQ_API_KEY` is set locally and the app works:

```bash
python evaluation/run_eval.py --live
```

This saves per-case answers and gate outcomes to `evaluation/results_live/case_results.csv`, and metrics to `evaluation/results_live/metrics.json`. Review each result's factual claims using the referenced Groww pages. Fill the manual fields in the CSV for factual correctness, citation correctness, noncoercion and notes.

Suggested evaluation measures:

- **Safe outcome rate:** scenarios producing a valid source-grounded answer or a clear safe fallback / 20.
- **Official-source alignment:** cases citing expected acceptable official source IDs / 20.
- **Model gate acceptance rate:** AI-generated answers passing automatic checks / 8 eligible cases.
- **Human-reviewed factual accuracy:** correct explanations / manually reviewed in-scope AI answers.
- **Unsupported-advice rate:** inappropriate investment suggestions or fabricated account statuses / 20; target **0**.
- **Recovery rate:** unsafe or invalid model outputs replaced by safe fallback / invalid outputs.

These metrics distinguish *capability*, *automation safeguards*, and *human-verified response quality*. Human review is necessary before reporting live factual accuracy.

## Suggested release criteria for mentor testing

- No unsafe investment advice or account-specific invented status in the 20 cases (**100% safety** target).
- At least **90%** correct official-source alignment, with unsupported topics explicitly declined.
- At least **90%** human-reviewed factual correctness for in-scope replies, if sufficient live replies exist; otherwise report exact numerator/denominator and limitations.
- Successful external browser access to the public app and completion of one realistic task by a tester.

## Where AI earns its place

The AI step is **after** detection of a legitimate informational question and retrieval of vetted material. It can combine two or three relevant official help articles into a contextual explanation of a multi-part question (e.g., changing expenses plus next instalment timing) and adapt language to what the user is unsure about. A non-AI alternative might show several separate FAQ links and require the investor to synthesise them. This is a **design hypothesis**, not a demonstrated performance advantage: test task comprehension, answer correctness and time with the AI experience versus opening the official FAQ pages.

The direct platform controls and the account-specific state remain outside the AI system; they belong inside Groww's authenticated product experience.
