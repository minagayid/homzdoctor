"""Integration test for the opt-in local model path."""

from __future__ import annotations

import asyncio
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from agents.llm_agent import LLMPatientAssistantAgent
from services.local_llm import LocalLLMClient


class _ChatHandler(BaseHTTPRequestHandler):
    request_body = None

    def do_POST(self):  # noqa: N802 - stdlib handler API
        length = int(self.headers["Content-Length"])
        _ChatHandler.request_body = json.loads(self.rfile.read(length))
        body = json.dumps(
            {"choices": [{"message": {"content": "Local explanation from gpt-oss."}}]}
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        return


class LocalLLMAgentTests(unittest.TestCase):
    def test_patient_assistant_uses_opt_in_local_backend(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), _ChatHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            endpoint = f"http://127.0.0.1:{server.server_port}/v1"
            agent = LLMPatientAssistantAgent(
                local_client=LocalLLMClient(endpoint=endpoint, model="gpt-oss-20b")
            )
            result = asyncio.run(agent.process({"query": "Explain my report."}))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(result["response"], "Local explanation from gpt-oss.")
        self.assertEqual(result["model"], "gpt-oss-20b")
        self.assertEqual(_ChatHandler.request_body["model"], "gpt-oss-20b")


if __name__ == "__main__":
    unittest.main()
