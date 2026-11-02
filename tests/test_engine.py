import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import load_kb, retrieve, safety_route, get_policy_answer, answer_question, validate_model_answer


class TestMVP(unittest.TestCase):
    def test_approved_sources_only(self):
        self.assertEqual(len(load_kb()), 6)
        self.assertTrue(all(d["url"].startswith("https://groww.in/help/") for d in load_kb()))

    def test_retrieval_edit(self):
        self.assertEqual(retrieve("Can I change my SIP amount?")[0]["topic"], "edit")

    def test_retrieval_payment(self):
        self.assertEqual(retrieve("My AutoPay debit failed")[0]["topic"], "payment")

    def test_retrieval_status(self):
        self.assertEqual(retrieve("Units are not showing after deduction")[0]["topic"], "status")

    def test_retrieval_skip(self):
        self.assertEqual(retrieve("Can I skip my SIP next month?")[0]["topic"], "skip")

    def test_retrieval_unsupported(self):
        self.assertEqual(retrieve("What is the best recipe for biryani?"), [])

    def test_no_password(self):
        self.assertEqual(safety_route("My password is abc. Log in"), "credentials")

    def test_no_otp(self):
        self.assertEqual(safety_route("Can I give you my OTP?"), "credentials")

    def test_no_pan(self):
        self.assertEqual(safety_route("Should I enter my PAN number?"), "credentials")

    def test_other_platform(self):
        self.assertEqual(safety_route("How do I edit SIP on Zerodha Coin?"), "other_platform")

    def test_investment_advice(self):
        self.assertEqual(safety_route("Which mutual fund should I buy for guaranteed returns?"), "investment_advice")

    def test_transaction(self):
        self.assertEqual(safety_route("Please pause my SIP immediately"), "transaction")

    def test_account_status(self):
        self.assertEqual(safety_route("Is my SIP active?"), "account_status")

    def test_invalid_model_citation(self):
        data = {"answer":"I recommend these next steps.","next_steps":[],"limits":"Verify in-app.","source_ids":["S99"]}
        self.assertIsNone(validate_model_answer(data, {"S1"}))

    def test_invalid_model_pressure(self):
        data = {"answer":"You must invest now to get guaranteed returns.","next_steps":[],"limits":"Verify.","source_ids":["S1"]}
        self.assertIsNone(validate_model_answer(data, {"S1"}))

    def test_without_key_safe_fallback(self):
        result = answer_question("My expenses are up, can I edit the SIP?", api_key=None)
        self.assertEqual(result["mode"], "documented_fallback")
        self.assertTrue(result["source_ids"])

    def test_blocked_queries_never_require_ai(self):
        result = answer_question("Which mutual fund should I buy?", api_key="not-a-real-key")
        self.assertEqual(result["mode"], "safety_fallback")

    def test_unknown_query_no_fake_answer(self):
        result = answer_question("Explain cricket bowling strategy", api_key=None)
        self.assertEqual(result["mode"], "no_match")

    def test_empty_question(self):
        self.assertEqual(answer_question("", api_key=None)["mode"], "safety_fallback")

    def test_golden_set_has_20_distinct_original_ids(self):
        import json
        data = json.loads((Path(__file__).resolve().parents[1] / "evaluation" / "golden_set_20_scenarios.json").read_text())
        self.assertEqual(len(data), 20)
        self.assertEqual(len({x["id"] for x in data}), 20)
        self.assertTrue(all(x["original_public_source"].startswith("https://") for x in data))

    def test_missing_holdings_use_supported_refusal(self):
        self.assertEqual(safety_route("My SIP holdings are missing and displayed total is lower"), "unsupported")

    def test_unsupported_scheme_subscription(self):
        self.assertEqual(safety_route("My SIP scheme has restricted new investments"), "unsupported")

    def test_specific_fund_advice_request(self):
        self.assertEqual(safety_route("Please recommend a specific fund"), "investment_advice")

    def test_personal_data_rejected(self):
        self.assertEqual(safety_route("My phone number is 9876543210"), "credentials")

    def test_hallucinated_url_rejected(self):
        data = {"answer":"Review this source http://unapproved-site.test for details.",
                "next_steps":[],"limits":"Verify.","source_ids":["S1"]}
        self.assertIsNone(validate_model_answer(data, {"S1"}))

    def test_fabricated_account_status_rejected(self):
        data = {"answer":"Your SIP is active and confirmed in the app.",
                "next_steps":[],"limits":"Verify.","source_ids":["S4"]}
        self.assertIsNone(validate_model_answer(data, {"S4"}))

    def test_valid_model_json_can_pass_gate(self):
        data = {"answer":"Groww describes an option to edit a SIP amount; check availability in your app.",
                "next_steps":["Review your SIP details."],"limits":"No account access.","source_ids":["S1"]}
        self.assertEqual(validate_model_answer(data, {"S1"})["mode"], "ai_grounded")


if __name__ == "__main__":
    unittest.main()
