from __future__ import annotations

import asyncio
import unittest

from core.request_limits import RequestBodyLimitMiddleware


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
        app_called = False
        messages = iter([
            {"type": "http.request", "body": b"123", "more_body": True},
            {"type": "http.request", "body": b"45", "more_body": False},
        ])

        async def app(scope, receive, send):
            nonlocal app_called
            app_called = True
            await receive()
            await receive()

        async def receive():
            return next(messages)

        async def send(message):
            sent.append(message)

        middleware = RequestBodyLimitMiddleware(app, max_body_bytes=4)
        asyncio.run(middleware({"type": "http", "headers": []}, receive, send))
        self.assertTrue(app_called)
        self.assertEqual(sent[0]["status"], 413)

    def test_path_specific_limit_applies_before_multipart_parser(self):
        called = False
        sent = []

        async def app(scope, receive, send):
            nonlocal called
            called = True

        async def send(message):
            sent.append(message)

        middleware = RequestBodyLimitMiddleware(
            app,
            max_body_bytes=100,
            path_limits={"/api/v1/users/me/avatar": 10},
        )
        asyncio.run(middleware(
            {
                "type": "http",
                "path": "/api/v1/users/me/avatar",
                "headers": [(b"content-length", b"11")],
            },
            lambda: None,
            send,
        ))
        self.assertFalse(called)
        self.assertEqual(sent[0]["status"], 413)


if __name__ == "__main__":
    unittest.main()
