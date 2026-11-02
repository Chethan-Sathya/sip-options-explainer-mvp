"""Mocked AI SDK responses to verify runtime gating, not live model accuracy."""
import json
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from engine import answer_question


def fake_groq_sdk(payload=None, error=None):
    def create(**kwargs):
        if error:
            raise error
        message = SimpleNamespace(content=json.dumps(payload))
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    return SimpleNamespace(Groq=lambda **kwargs: SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    ))


class TestMockModelGate(unittest.TestCase):
    def test_accepts_valid_structured_source_referenced_ai_answer(self):
        payload = {
            "answer": "Groww documents editing an SIP amount or date. Check available controls in the official app.",
            "next_steps": ["Review your SIP details and applicable conditions."],
            "limits": "This prototype cannot change a SIP.",
            "source_ids": ["S1"],
        }
        with patch.dict(sys.modules, {"groq": fake_groq_sdk(payload)}):
            result = answer_question("How can I edit my Groww SIP amount?", api_key="mock-not-a-real-key")
        self.assertEqual(result["mode"], "ai_grounded")
        self.assertEqual(result["source_ids"], ["S1"])

    def test_digit_supported_by_word_in_cited_source(self):
        payload = {
            "answer": "Groww says changes within 2 working days may apply to a later instalment; verify your SIP in the app.",
            "next_steps": ["Review the changes in your SIP details."],
            "limits": "This is not a personal financial recommendation.",
            "source_ids": ["S1"],
        }
        with patch.dict(sys.modules, {"groq": fake_groq_sdk(payload)}):
            result = answer_question("How can I edit my Groww SIP amount?", api_key="mock-not-a-real-key")
        self.assertEqual(result["mode"], "ai_grounded")

    def test_provider_error_classified_without_leaking_sensitive_text(self):
        error = RuntimeError("PRIVATE SECRET MUST NEVER BE SHOWN")
        error.status_code = 429
        with patch.dict(sys.modules, {"groq": fake_groq_sdk(error=error)}):
            result = answer_question("How can I edit my Groww SIP amount?", api_key="mock-not-a-real-key")
        self.assertEqual(result["mode"], "documented_fallback")
        self.assertIn("rate limit", result["gate_reason"])
        self.assertNotIn("PRIVATE SECRET", json.dumps(result))

    def test_groq_strict_response_format(self):
        from engine import groq_response_format
        fmt = groq_response_format({"S1", "S2"})
        self.assertEqual(fmt["type"], "json_schema")
        self.assertTrue(fmt["json_schema"]["strict"])
        self.assertEqual(fmt["json_schema"]["schema"]["properties"]["source_ids"]["items"]["enum"], ["S1", "S2"])

    def test_unverified_numeric_deadline_fails_closed(self):
        payload = {
            "answer": "Groww will always process your SIP edit in 14 working days.",
            "next_steps": [], "limits": "Check the app.", "source_ids": ["S1"],
        }
        with patch.dict(sys.modules, {"groq": fake_groq_sdk(payload)}):
            result = answer_question("How can I edit my Groww SIP amount?", api_key="mock-not-a-real-key")
        self.assertEqual(result["mode"], "documented_fallback")
        self.assertIn("failed", result["gate_reason"].lower())

    def test_invalid_citation_fails_closed(self):
        payload = {
            "answer": "I can promise an unsupported new option for your SIP.",
            "next_steps": [], "limits": "Check the app", "source_ids": ["FAKE999"]
        }
        with patch.dict(sys.modules, {"groq": fake_groq_sdk(payload)}):
            result = answer_question("How can I edit my Groww SIP amount?", api_key="mock-not-a-real-key")
        self.assertEqual(result["mode"], "documented_fallback")
        self.assertIn("failed", result["gate_reason"].lower())

    def test_api_exception_fails_closed_without_leaking_internal_message(self):
        with patch.dict(sys.modules, {"groq": fake_groq_sdk(error=RuntimeError("PRIVATE TEST PROVIDER FAILURE"))}):
            result = answer_question("How can I edit my Groww SIP amount?", api_key="mock-not-a-real-key")
        self.assertEqual(result["mode"], "documented_fallback")
        self.assertNotIn("PRIVATE TEST", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
