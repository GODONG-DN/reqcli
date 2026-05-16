"""Request history — stored locally in JSON."""

from __future__ import annotations

import json
import time
from pathlib import Path

from rich.console import Console
from rich.table import Table

HISTORY_FILE = Path.cwd() / ".req" / "history.json"
MAX_HISTORY = 200


def _load() -> list[dict]:
    if HISTORY_FILE.exists():
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    return []


def _save(data: list[dict]) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def add_to_history(method: str, url: str, status: int, elapsed: float) -> None:
    entries = _load()
    entries.insert(
        0,
        {
            "method": method.upper(),
            "url": url,
            "status": status,
            "elapsed_ms": round(elapsed * 1000),
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
    )
    _save(entries[:MAX_HISTORY])


def list_history(console: Console, search: str | None = None) -> None:
    entries = _load()

    if search:
        q = search.lower()
        entries = [e for e in entries if q in e["url"].lower() or str(e["status"]) == q]

    if not entries:
        console.print("[dim]No history yet. Make a request first![/]")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("#")
    table.add_column("Method")
    table.add_column("URL", style="cyan", no_wrap=False)
    table.add_column("Status")
    table.add_column("Time")
    table.add_column("When")

    for i, e in enumerate(entries[:50], 1):
        status_color = "green" if 200 <= e["status"] < 300 else "yellow" if e["status"] < 500 else "red"
        table.add_row(
            str(i),
            e["method"],
            e["url"][:80],
            f"[{status_color}]{e['status']}[/]",
            f"{e['elapsed_ms']}ms",
            e["time"],
        )

    console.print()
    console.print(table)
    console.print(f"[dim]{min(len(entries), 50)} entries shown[/]\n")


def clear_history(console: Console) -> None:
    _save([])
    console.print("[green]History cleared[/]")
