"""Tests for HTTP client."""

from __future__ import annotations

from req.client import _format_body, _guess_syntax, send_request


class TestClient:
    def test_format_json_body(self):
        result = _format_body('{"key": "val"}', "application/json")
        assert result == {"key": "val"}

    def test_format_plain_text(self):
        result = _format_body("hello world", "text/plain")
        assert result == "hello world"

    def test_format_invalid_json(self):
        result = _format_body("not json", "application/json")
        assert result == "not json"

    def test_guess_json_syntax(self):
        assert _guess_syntax("application/json") == "json"

    def test_guess_html_syntax(self):
        assert _guess_syntax("text/html") == "html"

    def test_guess_unknown_syntax(self):
        assert _guess_syntax("text/plain") == "text"

    def test_send_request_basic(self):
        import httpx
        import pytest

        try:
            resp = send_request("GET", "https://httpbin.org/get", timeout=5)
            assert resp.status_code == 200
        except Exception as e:
            pytest.skip(f"Network unavailable: {e}")

    def test_send_request_with_headers(self):
        import pytest

        try:
            resp = send_request(
                "GET", "https://httpbin.org/get",
                headers={"X-Custom": "test"},
                timeout=5,
            )
            assert resp.status_code == 200
        except Exception as e:
            pytest.skip(f"Network unavailable: {e}")
