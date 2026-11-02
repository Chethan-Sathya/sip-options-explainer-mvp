# Run the LIVE Golden Set evaluation — GitHub Actions

This is a **manual** workflow that calls the Groq model on the **8 eligible scenarios** from the 20 Evidence Log-derived Golden Set prompts. The other 12 scenarios test deterministic safety and refusal behaviour. A recoverable model answer may be retried once, so the total number of API calls can exceed eight.

## One-time setup

1. Open the repository **Settings → Secrets and variables → Actions**.
2. Choose **New repository secret**.
3. Secret name: `GROQ_API_KEY` (exactly).
4. Secret value: your existing Groq key from the Groq console. This is **separate** from the secret stored in Streamlit Community Cloud. Never paste it into a public GitHub file, commit, issue, PR, slide or chat.
5. Save.

## Run

1. Open **Actions** in the GitHub repository.
2. Select **Run LIVE Golden Set evaluation** in the left sidebar.
3. Choose **Run workflow**, branch `main`, then **Run workflow**.
4. Open the newly started workflow, then **live-evaluation** to inspect the result.
5. If successful, the run's **Summary** reports the number of passing scenarios and accepted AI-generated answers.
6. Under **Artifacts**, download `sip-live-golden-set-results`, unzip it and open `case_results.csv` and `metrics.json`.
7. Manually verify the actual AI answers against the linked official Groww help pages. Record **Yes/No/Unclear** in the manual review fields of `case_results.csv`. Do not mark an answer correct solely because it passed the automated gate.

## What the numbers mean

- **Automated pass rate:** Whether routing, approved citation IDs and obvious prohibited phrases passed (not semantic correctness).
- **AI acceptance:** How many of the eight eligible scenarios produced AI-generated answers accepted by the gate. A safe fallback is not an accepted AI answer.
- **Factual accuracy:** A separate, manually scored numerator/denominator after checking each AI explanation and its citations against the actual official page.
- **Safety:** Check that neither AI nor fallback recommends a fund, invents account information, requests credentials or coerces investment.

The prior **90% theme-label agreement** measures a different task (the Discovery Engine) and should not be reused as this MVP's factual accuracy. The scenarios are derived from public records and are not representative of all investors.

## Store and cite the evidence

Upload the exported results and the annotated CSV to the existing Drive Evidence Hub under `05_MVP_and_Evaluation`, excluding any account secrets. Take one screenshot of the GitHub run Summary and use the exact observed values in Slide 8.

The public Streamlit MVP remains available separately at:
https://sip-options-explainer-mvp-zwssjr7beycc9oznedyydc.streamlit.app/
