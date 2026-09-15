from __future__ import annotations

import asyncio
import unittest

from inference.request_limits import RequestBodyLimitMiddleware


class RequestBodyLimitMiddlewareTests(unittest.TestCase):
    def test_rejects_oversized_declared_body_before_calling_app(self):
        called = False
        sent = []

        async def app(scope, receive, send):
            nonlocal called
            called = True

        async def send(message):
            sent.append(message)

        middleware = RequestBodyLimitMiddleware(app, max_body_bytes=4)
        asyncio.run(middleware(
            {"type": "http", "headers": [(b"content-length", b"5")]},
            lambda: None,
            send,
        ))
        self.assertFalse(called)
        self.assertEqual(sent[0]["status"], 413)

    def test_caps_streamed_body_without_content_length(self):
        sent = []
        messages = iter([
            {"type": "http.request", "body": b"123", "more_body": True},
            {"type": "http.request", "body": b"45", "more_body": False},
        ])

        async def app(scope, receive, send):
            await receive()
            await receive()

        async def receive():
            return next(messages)

        async def send(message):
            sent.append(message)

        middleware = RequestBodyLimitMiddleware(app, max_body_bytes=4)
        asyncio.run(middleware({"type": "http", "headers": []}, receive, send))
        self.assertEqual(sent[0]["status"], 413)


if __name__ == "__main__":
    unittest.main()
