"""Protocol tests against a simulated FreeLLMAPI; no provider or model is contacted."""

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from services.local_llm import LocalLLMClient, LocalLLMUnavailable


class Handler(BaseHTTPRequestHandler):
    calls = []
    code = 200
    reply = {"choices": [{"message": {"content": "simulated response"}}]}

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        self.__class__.calls.append((self.path, self.headers.get("Authorization"), json.loads(self.rfile.read(length))))
        response = json.dumps(self.__class__.reply).encode()
        self.send_response(self.__class__.code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, *_args):
        pass


class FreeLLMAPICompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        Handler.calls = []
        Handler.code = 200
        Handler.reply = {"choices": [{"message": {"content": "simulated response"}}]}
        self.client = LocalLLMClient(endpoint=f"http://127.0.0.1:{self.server.server_port}/v1", model="auto", api_key="test-unified-key")

    def test_auto_model_and_bearer_key_are_sent_to_chat_endpoint(self):
        self.assertEqual(self.client.complete([{"role": "user", "content": "synthetic test"}]), "simulated response")
        path, authorization, body = Handler.calls[0]
        self.assertEqual(path, "/v1/chat/completions")
        self.assertEqual(authorization, "Bearer test-unified-key")
        self.assertEqual(body["model"], "auto")
        self.assertEqual(body["messages"], [{"role": "user", "content": "synthetic test"}])
        self.assertFalse(body["stream"])

    def test_rate_limit_is_reported_as_unavailable(self):
        Handler.code = 429
        with self.assertRaises(LocalLLMUnavailable):
            self.client.complete([{"role": "user", "content": "synthetic test"}])

    def test_empty_response_is_not_accepted_as_success(self):
        Handler.reply = {"choices": [{"message": {"content": ""}}]}
        with self.assertRaises(LocalLLMUnavailable):
            self.client.complete([{"role": "user", "content": "synthetic test"}])
