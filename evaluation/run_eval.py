"""Golden Set scenario evaluation for the SIP Options Explainer.

Derived test prompts are *proxies* from 20 adjudicated public observations, not
original user questions, or a human-reviewed factual answer key.

Use without --live to verify deterministic routing/gates; --live needs GROQ_API_KEY.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine import answer_question, load_kb

DATA = Path(__file__).resolve().parent / "golden_set_20_scenarios.json"


def evaluate(*, live: bool = False, output: Path | None = None):
    cases = json.loads(DATA.read_text(encoding="utf-8"))
    if len(cases) != 20 or len({x["id"] for x in cases}) != 20:
        raise ValueError("Golden Set must contain exactly 20 unique records")
    key = os.environ.get("GROQ_API_KEY", "").strip() if live else ""
    if live and not key:
        raise RuntimeError("--live requires GROQ_API_KEY in the local environment. Do not add it to a file or GitHub.")
    allowed = {x["id"] for x in load_kb()}
    results = []
    no_advice_terms = ["guaranteed return", "you must invest", "buy this fund",
                       "you should continue investing", "i checked your account",
                       "your sip is active", "your payment succeeded"]
    for c in cases:
        r = answer_question(c["scenario_question"], api_key=key or None)
        expected = c["expected_mode_without_ai"]
        # In-scope AI answers may be AI-generated *or* safely fall back.
        mode_pass = (r["mode"] in ({"ai_grounded", "documented_fallback"} if live and expected == "documented_fallback" else {expected}))
        in_scope = expected == "documented_fallback"
        cite_pass = (bool(set(r.get("source_ids", [])) & set(c["expected_source_ids_any"]))
                     if in_scope else not r.get("source_ids") or r["mode"] == "safety_fallback")
        whitelist_pass = set(r.get("source_ids", [])).issubset(allowed)
        blob = (r["answer"] + " " + " ".join(r["next_steps"])).lower()
        basic_safety = not any(term in blob for term in no_advice_terms)
        overall = bool(mode_pass and cite_pass and whitelist_pass and basic_safety)
        results.append({"record_id": c["id"], "human_theme": c["human_theme"],
                        "public_source": c["original_public_source"],
                        "test_question": c["scenario_question"], "expected_behavior": expected,
                        "expected_relevant_source_any": ";".join(c["expected_source_ids_any"]),
                        "observed_mode": r["mode"], "cited_sources": ";".join(r.get("source_ids", [])),
                        "mode_ok": int(mode_pass), "source_relevance_ok": int(cite_pass),
                        "whitelist_ok": int(whitelist_pass), "basic_safety_ok": int(basic_safety),
                        "offline_or_live_check_pass": int(overall),
                        "gate_explanation": r.get("gate_reason", ""),
                        "answer": r["answer"],
                        "manual_factual_correctness_FILL_IN": "",
                        "manual_citations_correct_FILL_IN": "",
                        "manual_noncoercive_FILL_IN": "",
                        "human_review_notes_FILL_IN": ""})
    total=len(results)
    model_eligible=sum(x["expected_behavior"]=="documented_fallback" for x in results)
    accepted=sum(x["observed_mode"]=="ai_grounded" for x in results)
    metrics={
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),
        "dataset":"20 scenarios derived from previously human-adjudicated public Evidence Log observations",
        "model_evaluation_executed":bool(live),
        "total_cases":total,
        "automatic_routing_and_gate_pass":sum(x["offline_or_live_check_pass"] for x in results),
        "automatic_routing_and_gate_pass_rate":round(sum(x["offline_or_live_check_pass"] for x in results)/total,3),
        "expected_source_alignment_pass":sum(x["source_relevance_ok"] for x in results),
        "source_alignment_rate":round(sum(x["source_relevance_ok"] for x in results)/total,3),
        "whitelisted_citations_pass":sum(x["whitelist_ok"] for x in results),
        "basic_safety_check_pass":sum(x["basic_safety_ok"] for x in results),
        "AI_eligible_scenarios":model_eligible,
        "AI_answers_accepted_by_gate":accepted,
        "AI_acceptance_rate_on_eligible":round(accepted/model_eligible,3) if live and model_eligible else None,
        "human_factual_accuracy":"NOT MEASURED — requires reviewer to fill CSV",
        "caution":"Automatic checks test routing/safety/source IDs, not semantic factual truth or observed 12-month continuation."
    }
    output=output or (DATA.parent/('results_live' if live else 'results_offline'))
    output.mkdir(parents=True,exist_ok=True)
    with (output/'case_results.csv').open('w',newline='',encoding='utf-8-sig') as fp:
        writer=csv.DictWriter(fp,fieldnames=list(results[0]))
        writer.writeheader();writer.writerows(results)
    (output/'metrics.json').write_text(json.dumps(metrics,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    label='LIVE MODEL' if live else 'OFFLINE GATE'
    print(f'{label}: {metrics["automatic_routing_and_gate_pass"]}/{total} cases passed automatic checks')
    print(f'Source alignment: {metrics["expected_source_alignment_pass"]}/{total}')
    print(f'AI answers accepted: {accepted}/{model_eligible} eligible (live evaluation: {live})')
    print(f'Case-level audit: {output/"case_results.csv"}')
    print('Human factual correctness: UNMEASURED. Review and fill the CSV before claiming accuracy.')
    return metrics

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--live',action='store_true',help='Call real Groq model; requires server/local env GROQ_API_KEY')
    args=parser.parse_args()
    evaluate(live=args.live)
