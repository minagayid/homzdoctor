"""Tests for the optional local OpenAI-compatible LLM connection."""

import unittest

from services.local_llm import (
    LocalLLMClient,
    LocalLLMUnavailable,
    build_chat_completion_payload,
)


class LocalLLMTests(unittest.TestCase):
    def test_disabled_client_is_explicitly_unavailable(self):
        client = LocalLLMClient(endpoint="", model="gpt-oss-20b")
        self.assertFalse(client.enabled)
        with self.assertRaises(LocalLLMUnavailable):
            client.complete([{"role": "user", "content": "hello"}])

    def test_endpoint_normalization_targets_openai_chat_completions(self):
        client = LocalLLMClient(endpoint="http://127.0.0.1:11434/v1/", model="gpt-oss-20b")
        self.assertEqual(client.chat_completions_url, "http://127.0.0.1:11434/v1/chat/completions")

    def test_payload_is_compatible_with_local_openai_servers(self):
        payload = build_chat_completion_payload(
            model="gpt-oss-20b",
            messages=[{"role": "user", "content": "Explain this report."}],
            max_tokens=120,
        )
        self.assertEqual(payload["model"], "gpt-oss-20b")
        self.assertEqual(payload["messages"][0]["content"], "Explain this report.")
        self.assertEqual(payload["max_tokens"], 120)
        self.assertFalse(payload["stream"])


if __name__ == "__main__":
    unittest.main()
