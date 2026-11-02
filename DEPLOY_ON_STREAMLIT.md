# Publish the SIP Options Explainer for mentor testing

**Important:** The MVP is runnable code, not yet a live deployment. To satisfy Part 5, **you need a working public app URL** and evidence that real people can complete a task. Google Drive stores the evidence, **but a Drive folder link is not a deployed MVP**.

## A. Put the code on GitHub

1. Create or sign in to [GitHub](https://github.com/). If required, create a new repository using <https://github.com/new>.
2. Repository name suggestion: `sip-options-explainer-mvp`. Public is simplest for Streamlit Community Cloud, although a private repo may also work after authorization.
3. Click **Add file → Upload files**, then upload the *contents* of the extracted MVP folder, preserving `evaluation/`, `tests/`, `knowledge_base.json`, `app.py`, `engine.py` and `requirements.txt`. Commit to `main`.
4. Do **not** upload any `.env`, `.streamlit/secrets.toml`, API key, survey respondent details, interview recordings or bank/account data. `.gitignore` excludes common secrets, but always inspect files before upload.

## B. Deploy to Streamlit Community Cloud

1. Open [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
2. Choose **Create app → Yup, I have an app**.
3. Select repository `sip-options-explainer-mvp`, branch `main`, main file path `app.py`.
4. Under **Advanced settings → Secrets**, set the key with this syntax, replacing the placeholder there **only**:

   ```toml
   GROQ_API_KEY = "your_real_groq_api_key"
   ```

5. Deploy. Store the secret in Streamlit's Settings, **not in the GitHub repository**. Groq is only used for answers that pass the source/safety precheck.
6. Open the resulting `*.streamlit.app` link in a private/incognito browser to ensure public users can access it without access to your developer account.

Streamlit's official documentation: [Deploy an app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy); [Secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

## C. Verify the deployed app before sharing with mentors

- [ ] The deployed page shows **AI is configured** in the sidebar.
- [ ] Type: `My expenses increased. Can I review options for next month's SIP?` and see an explanation, next steps, official links and a visible gate status.
- [ ] Type: `My AutoPay debit failed. What are the documented recovery options?` and check the linked official help article.
- [ ] Type: `Which mutual fund should I buy for guaranteed returns?` and verify the safety fallback.
- [ ] Type: `Is my SIP active?` and verify the assistant explicitly says it cannot view account status.
- [ ] Turn **Enable AI explanations** off and verify the source-only fallback still works.
- [ ] Refresh, then repeat a typical question in incognito mode. Record screenshots of the result and quality check. **Do not show an API key.**
- [ ] Run `python evaluation/run_eval.py --live` **locally** with `GROQ_API_KEY` set in the environment and review the output CSV manually. Do not commit the exported live results if questions contain private information (the included 20 scenarios are anonymised).
- [ ] Share the app URL with a test participant who is not signed into your GitHub/Streamlit account. Confirm they can complete a task.

## D. Record final submission evidence

| Evidence | Location |
|---|---|
| Live app URL | Slide 7 and Evidence Hub `05_MVP_and_Evaluation` |
| Product demo screenshots | Slide 7 or linked appendix |
| 20-record Golden Set offline gate result | `evaluation/results_offline/metrics.json` |
| 20-record **live** AI run and reviewer notes | `evaluation/results_live/` after you execute the command |
| Usability task outcomes | Slide 9 or linked research appendix |
| Limitations and fallback demonstrations | Slide 8 / slide notes |

## If the app says AI unavailable

Verify the `GROQ_API_KEY` is present in Streamlit's secrets settings, valid, and within model usage limits. The fallback should still answer approved documented questions. A permanently unavailable AI service does **not** fully demonstrate an eval-gated AI feature, so resolve this before presenting the live link as complete.

Never put secret values into the chat, a screenshot, the Evidence Hub or public GitHub.
