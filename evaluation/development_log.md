# Developer evaluation log — 2 November 2026

- 20 scenarios constructed from the original 20 human-adjudicated public Evidence Log records (SIP IDs retained).
- First offline pass: **17/20** expected routing + reference outcomes.
- Corrections: SIP005 (missing holdings) now refuses unsupported account-data claim; SIP009 (scheme subscription restriction) now refuses unsupported scheme-specific guidance; SIP014 (request for a 'specific fund') now triggers no-investment-advice policy.
- Second offline pass: **20/20** expected outcomes. This is an iterative developer regression result, not an independent blind evaluation.
- Real Groq inference: **not exercised here** (no key supplied in this environment).
- Human factual review: **not performed**.
- Production URL: **not yet provisioned**; deployment through a connected GitHub/Streamlit account remains necessary.

- 2026-11-02: Verified 31/31 unit tests and 20/20 offline scenario gates; added guard blocking unsupported numeric deadline claims, updated offline AI acceptance to N/A. Live provider and public Streamlit deployment remain untested.
