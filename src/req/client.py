"""HTTP client — makes requests and formats responses beautifully."""

from __future__ import annotations

import json
import time
from typing import Any

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax


def _format_body(content: str, content_type: str) -> Any:
    """Try to pretty-print the response body."""
    ct = content_type.lower()
    if "json" in ct:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content
    return content


def _guess_syntax(content_type: str) -> str:
    ct = content_type.lower()
    if "json" in ct:
        return "json"
    if "html" in ct:
        return "html"
    if "xml" in ct:
        return "xml"
    if "javascript" in ct:
        return "javascript"
    if "css" in ct:
        return "css"
    return "text"


def send_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json_body: Any = None,
    data: dict | None = None,
    params: dict | None = None,
    auth_bearer: str | None = None,
    auth_basic: tuple[str, str] | None = None,
    timeout: float = 30,
    verify: bool = True,
) -> httpx.Response:
    """Send an HTTP request and return the response."""

    _headers = dict(headers or {})
    if auth_bearer:
        _headers["Authorization"] = f"Bearer {auth_bearer}"
    if auth_basic:
        import base64

        creds = base64.b64encode(f"{auth_basic[0]}:{auth_basic[1]}".encode()).decode()
        _headers["Authorization"] = f"Basic {creds}"

    client = httpx.Client(verify=verify, timeout=timeout, follow_redirects=True)
    resp = client.request(
        method=method.upper(),
        url=url,
        headers=_headers or None,
        json=json_body,
        data=data,
        params=params,
    )
    return resp


def print_response(
    console: Console,
    resp: httpx.Response,
    elapsed: float,
    *,
    silent: bool = False,
) -> None:
    """Pretty-print an HTTP response."""

    if silent:
        if resp.content:
            console.print(resp.text)
        return

    status_color = "green" if 200 <= resp.status_code < 300 else "yellow" if resp.status_code < 500 else "red"
    size = len(resp.content)
    console.print()
    console.print(
        f"  [bold {status_color}]HTTP {resp.http_version} {resp.status_code} {resp.reason_phrase}[/] "
        f"[dim]{size} bytes in {elapsed*1000:.0f}ms[/]"
    )

    if resp.headers:
        console.print()
        for key, val in resp.headers.items():
            console.print(f"  [dim]{key}:[/] {val}")

    if resp.content:
        content_type = resp.headers.get("content-type", "")
        body = resp.text
        fmt = _format_body(body, content_type)

        console.print()
        if isinstance(fmt, (dict, list)):
            syntax = Syntax(
                json.dumps(fmt, indent=2, ensure_ascii=False),
                "json",
                theme="monokai",
                background_color="default",
            )
            console.print(syntax)
        else:
            lang = _guess_syntax(content_type)
            if len(body) > 5000:
                body = body[:5000] + f"\n\n[dim]... truncated ({len(resp.content)} bytes total)[/]"
            syntax = Syntax(body, lang, theme="monokai", background_color="default")
            console.print(syntax)

    console.print()


def export_curl(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json_body: Any = None,
    data: dict | None = None,
) -> str:
    """Export a request as a curl command."""
    parts = ["curl", "-X", method.upper()]

    if headers:
        for k, v in headers.items():
            parts.extend(["-H", f"{k}: {v}"])

    if json_body is not None:
        parts.extend(["-H", "Content-Type: application/json"])
        parts.extend(["-d", json.dumps(json_body, ensure_ascii=False)])
    elif data:
        for k, v in data.items():
            parts.extend(["-d", f"{k}={v}"])

    parts.append(url)

    import shlex
    return " ".join(shlex.quote(p) for p in parts)
