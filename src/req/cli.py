"""Req CLI — terminal API client."""

from __future__ import annotations

import time
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from req.client import export_curl, print_response, send_request
from req.state import extract_value, set_state, substitute_state
from req.collection import (
    add_request,
    init_collection,
    list_collection,
    run_collection,
)
from req.env import (
    delete_var,
    export_dotenv,
    get_var,
    list_vars,
    load_dotenv,
    set_var,
    substitute,
)
from req.history import add_to_history, clear_history, list_history

app = typer.Typer(
    name="req",
    help="Terminal API client — like Postman, but in your terminal",
    no_args_is_help=True,
)

console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold]req[/] version [cyan]{__import__('req').__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=_version_callback, is_eager=True
    ),
) -> None:
    pass


@app.command()
def get(
    url: str = typer.Argument(..., help="URL or path to request"),
    auth: str = typer.Option(None, "--auth", "-a", help="Bearer token or user:pass"),
    headers: list[str] = typer.Option(None, "--header", "-H", help="Custom header (key:value)"),
    query: list[str] = typer.Option(None, "--query", "-q", help="Query param (key=value)"),
    timeout: float = typer.Option(30, "--timeout", help="Request timeout in seconds"),
    insecure: bool = typer.Option(False, "--insecure", "-k", help="Skip SSL verification"),
    silent: bool = typer.Option(False, "--silent", "-s", help="Print only the response body"),
    export: bool = typer.Option(False, "--export", "-e", help="Export as curl command instead of sending"),
    extract: str = typer.Option(None, "--extract", "-x", help="Extract a JSON field from the response"),
) -> None:
    """Send a GET request."""
    _do_request("GET", url, auth=auth, headers=headers, query=query, timeout=timeout, insecure=insecure, silent=silent, export=export, extract=extract)


@app.command()
def post(
    url: str = typer.Argument(..., help="URL or path to request"),
    json_body: str = typer.Option(None, "--json", "-j", help="JSON body (inline or @file)"),
    data: list[str] = typer.Option(None, "--data", "-d", help="Form data (key=value)"),
    auth: str = typer.Option(None, "--auth", "-a", help="Bearer token or user:pass"),
    headers: list[str] = typer.Option(None, "--header", "-H", help="Custom header (key:value)"),
    query: list[str] = typer.Option(None, "--query", "-q", help="Query param (key=value)"),
    timeout: float = typer.Option(30, "--timeout", help="Request timeout in seconds"),
    insecure: bool = typer.Option(False, "--insecure", "-k", help="Skip SSL verification"),
    silent: bool = typer.Option(False, "--silent", "-s", help="Print only the response body"),
    export: bool = typer.Option(False, "--export", "-e", help="Export as curl command"),
    extract: str = typer.Option(None, "--extract", "-x", help="Extract a JSON field from the response"),
) -> None:
    """Send a POST request."""
    _do_request(
        "POST", url, json_body=json_body, data=data, auth=auth, headers=headers,
        query=query, timeout=timeout, insecure=insecure, silent=silent, export=export, extract=extract,
    )


@app.command()
def put(
    url: str = typer.Argument(..., help="URL or path to request"),
    json_body: str = typer.Option(None, "--json", "-j", help="JSON body"),
    auth: str = typer.Option(None, "--auth", "-a", help="Bearer token or user:pass"),
    headers: list[str] = typer.Option(None, "--header", "-H", help="Custom header (key:value)"),
    timeout: float = typer.Option(30, "--timeout", help="Request timeout in seconds"),
    insecure: bool = typer.Option(False, "--insecure", "-k", help="Skip SSL verification"),
    silent: bool = typer.Option(False, "--silent", "-s", help="Print only the response body"),
    export: bool = typer.Option(False, "--export", "-e", help="Export as curl command"),
) -> None:
    """Send a PUT request."""
    _do_request("PUT", url, json_body=json_body, auth=auth, headers=headers, timeout=timeout, insecure=insecure, silent=silent, export=export)


@app.command()
def patch(
    url: str = typer.Argument(..., help="URL or path to request"),
    json_body: str = typer.Option(None, "--json", "-j", help="JSON body"),
    auth: str = typer.Option(None, "--auth", "-a", help="Bearer token or user:pass"),
    headers: list[str] = typer.Option(None, "--header", "-H", help="Custom header (key:value)"),
    timeout: float = typer.Option(30, "--timeout", help="Request timeout in seconds"),
    insecure: bool = typer.Option(False, "--insecure", "-k", help="Skip SSL verification"),
    silent: bool = typer.Option(False, "--silent", "-s", help="Print only the response body"),
    export: bool = typer.Option(False, "--export", "-e", help="Export as curl command"),
) -> None:
    """Send a PATCH request."""
    _do_request("PATCH", url, json_body=json_body, auth=auth, headers=headers, timeout=timeout, insecure=insecure, silent=silent, export=export)


@app.command()
def delete(
    url: str = typer.Argument(..., help="URL or path to request"),
    auth: str = typer.Option(None, "--auth", "-a", help="Bearer token or user:pass"),
    headers: list[str] = typer.Option(None, "--header", "-H", help="Custom header (key:value)"),
    timeout: float = typer.Option(30, "--timeout", help="Request timeout in seconds"),
    insecure: bool = typer.Option(False, "--insecure", "-k", help="Skip SSL verification"),
    silent: bool = typer.Option(False, "--silent", "-s", help="Print only the response body"),
    export: bool = typer.Option(False, "--export", "-e", help="Export as curl command"),
) -> None:
    """Send a DELETE request."""
    _do_request("DELETE", url, auth=auth, headers=headers, timeout=timeout, insecure=insecure, silent=silent, export=export)


def _do_request(
    method: str,
    url: str,
    *,
    json_body: str | None = None,
    data: list[str] | None = None,
    auth: str | None = None,
    headers: list[str] | None = None,
    query: list[str] | None = None,
    timeout: float = 30,
    insecure: bool = False,
    silent: bool = False,
    export: bool = False,
    extract: str | None = None,
) -> None:
    """Core request dispatcher."""

    url = substitute(substitute_state(url))

    # Parse headers
    req_headers: dict[str, str] = {}
    if headers:
        for h in headers:
            if ":" in h:
                k, v = h.split(":", 1)
                req_headers[k.strip()] = v.strip()

    # Parse query params
    req_params: dict[str, str] = {}
    if query:
        for q in query:
            if "=" in q:
                k, v = q.split("=", 1)
                req_params[k.strip()] = v.strip()

    # Parse auth
    bearer = None
    basic = None
    if auth:
        if ":" in auth:
            user, passwd = auth.split(":", 1)
            basic = (user, passwd)
        else:
            bearer = auth

    # Parse body
    parsed_body: Any = None
    if json_body:
        import json as _json
        if json_body.startswith("@"):
            path = json_body[1:]
            parsed_body = _json.loads(open(path, encoding="utf-8").read())
        else:
            try:
                parsed_body = _json.loads(json_body)
            except _json.JSONDecodeError:
                parsed_body = json_body

    parsed_data: dict | None = None
    if data:
        parsed_data = {}
        for d in data:
            if "=" in d:
                k, v = d.split("=", 1)
                parsed_data[k.strip()] = v.strip()

    # Export as curl
    if export:
        if basic:
            req_headers["Authorization"] = "Basic ..."
        elif bearer:
            req_headers["Authorization"] = f"Bearer {bearer}"
        curl_cmd = export_curl(method, url, headers=req_headers, json_body=parsed_body, data=parsed_data)
        console.print(f"[dim]{curl_cmd}[/]")
        return

    # Send
    start = time.time()
    try:
        resp = send_request(
            method, url,
            headers=req_headers, json_body=parsed_body, data=parsed_data,
            params=req_params, auth_bearer=bearer, auth_basic=basic,
            timeout=timeout, verify=not insecure,
        )
    except Exception as exc:
        msg = str(exc).lower()
        if "name or service not known" in msg or "getaddrinfo" in msg:
            console.print(f"[red]DNS lookup failed:[/] {url.split('/')[2] if '://' in url else url}")
            console.print(f"[dim]Check the hostname or your internet connection.[/]")
        elif "timeout" in msg or "timed out" in msg:
            console.print(f"[red]Request timed out:[/] {url}")
            console.print(f"[dim]The server didn't respond in {timeout}s. Try --timeout for longer waits.[/]")
        elif "certificate" in msg or "ssl" in msg:
            console.print(f"[red]SSL error:[/] {url}")
            console.print(f"[dim]Use -k to skip certificate verification (insecure).[/]")
        elif "connection" in msg:
            console.print(f"[red]Connection failed:[/] {url}")
            console.print(f"[dim]The server might be down or unreachable.[/]")
        else:
            console.print(f"[red]Request failed:[/] {exc}")
        return
    elapsed = time.time() - start

    print_response(console, resp, elapsed, silent=silent)
    add_to_history(method, url, resp.status_code, elapsed)

    if extract and resp.content:
        val = extract_value(resp.text, extract)
        if val:
            set_state(extract, val)
            console.print(f"  [dim]Extracted [cyan]{extract}[/] = {val[:80]}[/]")


# -------------------------------------------------------
#  env
# -------------------------------------------------------

@app.command()
def env(
    action: str = typer.Argument("list", help="list|set|get|delete|load|export"),
    key: str = typer.Argument(None, help="Variable key or file path"),
    value: str = typer.Argument(None, help="Variable value"),
) -> None:
    """Manage environment variables for the current project."""
    if action == "list":
        list_vars(console)
    elif action == "set" and key and value:
        set_var(console, key, value)
    elif action == "get" and key:
        get_var(console, key)
    elif action == "delete" and key:
        delete_var(console, key)
    elif action == "load":
        load_dotenv(console, path=key)
    elif action == "export":
        export_dotenv(console, path=key)
    else:
        console.print("[dim]Usage: req env [list|set KEY VAL|get KEY|delete KEY|load .env|export .env][/]")


# -------------------------------------------------------
#  history
# -------------------------------------------------------

@app.command()
def history(
    search_term: str = typer.Argument(None, help="Filter history by URL or status"),
    clear: bool = typer.Option(False, "--clear", help="Clear all history"),
) -> None:
    """View request history."""
    if clear:
        clear_history(console)
        return

    list_history(console, search_term)


# -------------------------------------------------------
#  collection
# -------------------------------------------------------

_collection = typer.Typer(help="Manage request collections")
app.add_typer(_collection, name="collection")


@_collection.command()
def init(
    name: str = typer.Argument("default", help="Collection name"),
) -> None:
    """Initialize a new request collection."""
    init_collection(console, name)


@_collection.command()
def add(
    name: str = typer.Argument(..., help="Request name"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP method"),
    path: str = typer.Option(..., "--path", "-p", help="URL path"),
    headers: list[str] = typer.Option(None, "--header", "-H", help="Header (key:value)"),
    json_body: str = typer.Option(None, "--json", "-j", help="JSON body"),
    expect_status: int = typer.Option(None, "--expect-status", help="Expected HTTP status code"),
    expect_contains: str = typer.Option(None, "--expect-contains", help="Text that response must contain"),
    expect_time: int = typer.Option(None, "--expect-time", help="Max response time in ms"),
) -> None:
    """Add a request to the collection."""
    add_request(
        console, name, method, path, headers=headers, json_body=json_body,
        expect_status=expect_status, expect_contains=expect_contains,
        expect_time_ms=expect_time,
    )


@_collection.command()
def ls() -> None:
    """List requests in the collection."""
    list_collection(console)


@_collection.command()
def run(
    index: int = typer.Option(None, "--index", "-i", help="Run a single request by number"),
    base_url: str = typer.Option("", "--base", "-b", help="Base URL to prefix all paths"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show response for every request"),
    insecure: bool = typer.Option(False, "--insecure", "-k", help="Skip SSL verification"),
) -> None:
    """Run all requests in the collection."""
    run_collection(console, index=index, base_url=base_url, verbose=verbose, insecure=insecure)


# -------------------------------------------------------
#  state
# -------------------------------------------------------

@app.command()
def state(
    clear: bool = typer.Option(False, "--clear", help="Clear all extracted state"),
) -> None:
    """View or clear request-chaining state (extracted values)."""
    from req.state import STATE_FILE, _load

    if clear:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text("{}")
        console.print("[green]State cleared[/]")
        return

    data = _load()
    if not data:
        console.print("[dim]No extracted state. Use --extract on a request to capture values.[/]")
        console.print("[dim]Then reference them with {{$key}} in subsequent requests.[/]")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    for k, v in data.items():
        table.add_row(k, v[:80])

    console.print()
    console.print(table)


# -------------------------------------------------------
#  test
# -------------------------------------------------------

@app.command()
def test(
    base_url: str = typer.Option("", "--base", "-b", help="Base URL to prefix all paths"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full response for failures"),
    insecure: bool = typer.Option(False, "--insecure", "-k", help="Skip SSL verification"),
) -> None:
    """Run collection requests with assertion checks."""
    run_collection(console, base_url=base_url, verbose=verbose, insecure=insecure)


if __name__ == "__main__":
    app()
