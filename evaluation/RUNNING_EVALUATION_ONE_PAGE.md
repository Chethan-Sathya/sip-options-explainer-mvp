# Evaluation one-page summary — 2 November 2026

- **Original discovery Golden Set:** 20 manually adjudicated public conversations; initial theme-label agreement 18/20 = 90%. That metric pertains only to the Discovery Engine.
- **MVP Golden Set:** each of those 20 IDs mapped to an illustrative scenario and expected response policy (8 in-scope / 12 safety or out of scope).
- **Baseline implementation:** 17/20 automatic route/reference outcomes; improved to 20/20 after three developer fixes.
- **Current evaluated offline outcome:** 20/20 automated routing, approved-source alignment and basic safety checks (100%). No Groq inference was used for the offline result.
- **Current AI output factual accuracy:** not measured — real API calls and human review are outstanding.
- **Current production status:** deployment outstanding; no verified public URL.

Run `python evaluation/run_eval.py --live` with server/local `GROQ_API_KEY`, then manually review and annotate each response in `evaluation/results_live/case_results.csv` before reporting the model's answer accuracy.

**User-visible quality gate:** checks policy before model call; passes only structurally valid, official-citation-linked, basic-safety-screened AI responses; otherwise shows a deterministic, explicitly labelled safe fallback. This is not a guarantee against every hallucination or financial misunderstanding.

**Non-AI comparison:** a static FAQ may expose relevant pages, while the AI explanation can combine multiple official documents and phrase a conditional answer to a multi-part SIP concern. Comparative user testing is needed to show whether the AI version actually improves comprehension.
