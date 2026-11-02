"""Streamlit front end for a non-transactional Groww SIP educational prototype."""
from __future__ import annotations

import os
import json
from pathlib import Path
import streamlit as st
from engine import MODEL, answer_question, attached_sources

st.set_page_config(page_title="SIP Options Explainer | Research MVP", page_icon="📘", layout="centered")

# Session state is temporary and never written to disk by this app.
if "question" not in st.session_state:
    st.session_state.question = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "ai_attempts" not in st.session_state:
    st.session_state.ai_attempts = 0
MAX_AI_ATTEMPTS_PER_SESSION = 12

st.title("SIP Options Explainer")
st.caption("A research MVP for understanding Groww mutual-fund SIP options · Not affiliated with Groww")
st.info("This is an educational prototype. It does not access your account, change SIPs, or provide investment advice. "
        "Do not enter passwords, OTPs, bank details, PAN, Aadhaar or identifying financial information.", icon="ℹ️")

with st.sidebar:
    st.subheader("Answer settings")
    use_ai = st.toggle("Enable AI explanations", value=True,
                       help="When off, only curated official-source explanations are used.")
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("GROQ_API_KEY", "")
        except (FileNotFoundError, KeyError):
            pass
    if use_ai and not key:
        st.warning("AI temporarily unavailable: no server key configured. The source-only fallback still works.")
    if use_ai and key:
        st.success("AI is configured; every output must pass the quality gate.")
        st.caption(f"AI requests remaining this session: {max(0, MAX_AI_ATTEMPTS_PER_SESSION - st.session_state.ai_attempts)}")
    st.caption("AI model: " + MODEL)
    st.caption("Build: diagnostics-2026-11-02")
    st.caption("No SIP actions or user account access are supported.")
    st.caption("Source excerpts reviewed: 2 Nov 2026. Confirm changing rules in the official app.")
    if st.button("Clear current question"):
        st.session_state.question = ""
        st.session_state.last_result = None
        st.rerun()

st.subheader("What would you like to understand?")
examples = [
    "My expenses increased this month. What SIP options can I review?",
    "My SIP AutoPay failed. What can I check?",
    "The bank deducted money, but units are not showing yet.",
]
cols = st.columns(3)
for col, sample in zip(cols, examples):
    with col:
        if st.button(sample, use_container_width=True):
            st.session_state.question = sample
            st.session_state.last_result = None

st.text_area("Your question", key="question", max_chars=600, height=110,
             placeholder="For example: Can I skip next month's SIP?")
if st.button("Explain my options", type="primary", use_container_width=True):
    with st.spinner("Reviewing official-source excerpts..."):
        ai_allowed = bool(use_ai and key and st.session_state.ai_attempts < MAX_AI_ATTEMPTS_PER_SESSION)
        if ai_allowed:
            st.session_state.ai_attempts += 1
        st.session_state.last_result = answer_question(
            st.session_state.question,
            api_key=key if ai_allowed else None,
        )
        if use_ai and key and not ai_allowed:
            st.session_state.last_result["gate_reason"] = "Session AI request limit reached; source-only fallback provided."

if st.session_state.last_result is not None:
    result = st.session_state.last_result
    st.divider()
    st.subheader("Explanation")
    st.markdown("**Visible quality check**")
    if result["mode"] == "ai_grounded":
        st.success("PASS · AI answer met automatic citation, structure and safety checks.")
    elif result["mode"] == "safety_fallback":
        st.info("SAFE FALLBACK · Question requires a boundary; AI was bypassed.")
    elif result["mode"] == "no_match":
        st.warning("NO VERIFIED SOURCE · The assistant did not invent an answer.")
    else:
        st.warning("SOURCE-ONLY FALLBACK · AI not available or did not pass the gate.")
    gate_reason = result.get("gate_reason", "No diagnostic was recorded.")
    if result["mode"] == "documented_fallback":
        st.error("Why this fallback happened: " + gate_reason, icon="🔎")
        if "authentication or permission" in gate_reason.lower():
            st.info("The server found a key, but Groq did not authorize the request. Verify the key in Streamlit App settings → Secrets without sharing it here.")
        elif "rate limit" in gate_reason.lower():
            st.info("Groq has reported a rate limit. Keep the safe answer; check your Groq usage and limits.")
        elif "provider rejected" in gate_reason.lower():
            st.info("The provider rejected the AI request format. This requires a code fix; do not remove the safety gate.")
        elif "failed automatic" in gate_reason.lower():
            st.info("Groq returned content, but it did not pass an automatic check. The safe source-only answer is intentional.")
        elif "service" in gate_reason.lower() or "network" in gate_reason.lower():
            st.info("The request could not complete. Do not share the API key; check whether the Groq account and deployment are operational.")
        st.caption("For support, share ONLY the text in the red diagnostic box, never your key or private account information.")
    else:
        st.caption(gate_reason)
    st.write(result["answer"])
    if result["next_steps"]:
        st.markdown("**Steps you may review independently**")
        for i, step in enumerate(result["next_steps"], start=1):
            st.write(f"{i}. {step}")
    st.caption(result["limits"])
    docs = attached_sources(result)
    if docs:
        st.markdown("**Official source links**")
        for doc in docs:
            st.markdown(f'- [{doc["title"]}]({doc["url"]}) (`{doc["id"]}`)')
        with st.expander("Which source material was used?"):
            for doc in docs:
                st.markdown(f'**{doc["id"]}: {doc["title"]}**')
                st.write(doc["summary"])
    else:
        st.markdown("[Official Groww Mutual Funds help centre](https://groww.in/help/mutual-funds)")
    st.caption("This is an automatic output gate, not a guarantee of factual correctness. References are not proof of your personal account status.")

st.divider()
with st.expander("Why use AI instead of a standard FAQ?"):
    st.write("The AI step is intended for multi-part questions requiring information from several approved help pages, "
             "such as changing expenses plus an upcoming payment date. It can adapt the explanation to the question; "
             "a non-AI FAQ list typically leaves users to assemble the answer themselves. This benefit is a hypothesis "
             "to be tested against a non-AI reference experience, not a demonstrated outcome.")

with st.expander("Golden Set quality evaluation — what has been measured"):
    metrics_path = Path(__file__).resolve().parent / "evaluation" / "results_offline" / "metrics.json"
    try:
        stats = json.loads(metrics_path.read_text(encoding="utf-8"))
        st.write(f"Automated offline routing/safety/source checks: {stats['automatic_routing_and_gate_pass']}/{stats['total_cases']} scenarios")
        st.write("Live AI model accuracy: **not measured**; a Groq-keyed evaluation and manual factual review are required.")
        st.caption("20 scenarios are derived from the original research Golden Set, not identical to the public posts. "
                   "This is a developer regression test, not a blind estimate of model quality.")
    except (OSError, ValueError, KeyError):
        st.write("Evaluation report not available. Consult the project evaluation protocol.")

with st.expander("About this research MVP and its limitations"):
    st.markdown(
        "- **Research status:** The financial-flexibility and SIP-support problems are still hypotheses. More user interviews are being collected.\n"
        "- **Scope:** Explains documented SIP options and status-checking routes; does not perform transactions.\n"
        "- **Reliability:** If AI is unavailable or produces an invalid answer, the app displays a source-grounded fallback.\n"
        "- **Privacy:** No account login or transaction data is requested. If AI is enabled, the question and approved help excerpts are sent to Groq for processing. Do not enter personal data.\n"
        "- **Sources:** A small, manually curated set of official Groww help articles, reviewed 2 Nov 2026. This is not a live Groww integration.\n"
        "- **Evaluation:** The 20 Golden Set-derived scenarios test routing and safeguards; live AI factual accuracy requires human review.\n"
        "- **Testing:** Deployment availability does not make this suitable for financial decisions."
    )
