"""Request collection manager — organize requests in JSON files."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from req.client import print_response, send_request
from req.env import substitute

COLLECTION_FILE = Path.cwd() / ".req" / "collection.json"


def _load() -> dict[str, Any]:
    if COLLECTION_FILE.exists():
        return json.loads(COLLECTION_FILE.read_text(encoding="utf-8"))
    return {"name": "default", "requests": []}


def _save(data: dict) -> None:
    COLLECTION_FILE.parent.mkdir(parents=True, exist_ok=True)
    COLLECTION_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def init_collection(console: Console, name: str) -> None:
    data = {"name": name, "requests": []}
    _save(data)
    console.print(f"[green]Collection [bold]{name}[/] initialized[/]")


def add_request(
    console: Console,
    name: str,
    method: str,
    path: str,
    *,
    headers: list[str] | None = None,
    json_body: str | None = None,
) -> None:
    data = _load()
    req_headers = {}
    if headers:
        for h in headers:
            if ":" in h:
                k, v = h.split(":", 1)
                req_headers[k.strip()] = v.strip()

    entry = {
        "name": name,
        "method": method.upper(),
        "path": path,
        "headers": req_headers,
    }
    if json_body:
        try:
            entry["body"] = json.loads(json_body)
        except json.JSONDecodeError:
            entry["body"] = json_body

    data["requests"].append(entry)
    _save(data)
    console.print(f"  [green]+[/] {method.upper()} {path} — {name}")


def list_collection(console: Console) -> None:
    data = _load()
    reqs = data.get("requests", [])

    if not reqs:
        console.print("[dim]No requests in collection. Use: req collection add[/]")
        return

    console.print(f"\n[bold]{data['name']}[/] ({len(reqs)} requests)")
    table = Table(show_header=True, header_style="bold")
    table.add_column("#")
    table.add_column("Method")
    table.add_column("Path", style="cyan")
    table.add_column("Name")

    for i, r in enumerate(reqs, 1):
        method_color = {
            "GET": "green",
            "POST": "yellow",
            "PUT": "blue",
            "PATCH": "magenta",
            "DELETE": "red",
        }.get(r["method"], "white")
        table.add_row(str(i), f"[{method_color}]{r['method']}[/]", r["path"], r["name"])

    console.print()
    console.print(table)


def run_collection(
    console: Console,
    *,
    index: int | None = None,
    base_url: str = "",
    verbose: bool = False,
    insecure: bool = False,
) -> None:
    data = _load()
    reqs = data.get("requests", [])

    if index is not None:
        if 1 <= index <= len(reqs):
            reqs = [reqs[index - 1]]
        else:
            console.print(f"[red]Invalid index:[/] {index}")
            return

    from rich.progress import Progress

    passed = 0
    failed = 0

    with Progress(transient=True) as progress:
        task = progress.add_task("Running...", total=len(reqs))

        for i, r in enumerate(reqs, 1):
            url = substitute(f"{base_url}{r['path']}")
            method = r["method"]

            try:
                start = time.time()
                resp = send_request(
                    method, url, headers=r.get("headers"), json_body=r.get("body"),
                    verify=not insecure,
                )
                elapsed = time.time() - start

                ok = 200 <= resp.status_code < 300

                if ok:
                    passed += 1
                    if verbose:
                        console.print(
                            f"  [green]OK[/] {method} {url} [{resp.status_code}] {elapsed*1000:.0f}ms"
                        )
                else:
                    failed += 1
                    console.print(
                        f"  [red]FAIL[/] {method} {url} [{resp.status_code}] {elapsed*1000:.0f}ms"
                    )
                    if verbose:
                        print_response(console, resp, elapsed)
            except Exception as exc:
                failed += 1
                console.print(f"  [red]ERR[/] {method} {url} — {exc}")

            progress.update(task, advance=1)

    console.print()
    total = passed + failed
    if failed == 0:
        console.print(f"  [green]All {total} passed[/]")
    else:
        console.print(f"  [yellow]{passed}/{total} passed[/] [red]{failed} failed[/]")
    console.print()
