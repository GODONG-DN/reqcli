"""Environment variable manager — scoped to current directory."""

from __future__ import annotations

import json
import os
from pathlib import Path

from rich.console import Console
from rich.table import Table

ENV_FILE = Path.cwd() / ".req" / "env.json"


def _ensure_dir() -> None:
    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load() -> dict[str, str]:
    if ENV_FILE.exists():
        return json.loads(ENV_FILE.read_text(encoding="utf-8"))
    return {}


def _save(data: dict[str, str]) -> None:
    _ensure_dir()
    ENV_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def substitute(url: str) -> str:
    """Replace {{VAR}} placeholders with env values."""
    env = _load()
    result = url
    for key, val in env.items():
        result = result.replace(f"{{{{{key}}}}}", val)
    return result


def set_var(console: Console, key: str, value: str) -> None:
    data = _load()
    data[key] = value
    _save(data)
    console.print(f"  [green]{key}[/] = {value}")


def get_var(console: Console, key: str) -> None:
    data = _load()
    if key in data:
        console.print(f"  {key} = {data[key]}")
    else:
        console.print(f"  [dim]{key} not set[/]")


def delete_var(console: Console, key: str) -> None:
    data = _load()
    if key in data:
        del data[key]
        _save(data)
        console.print(f"  [red]Removed[/] {key}")


def list_vars(console: Console) -> None:
    data = _load()
    if not data:
        console.print("[dim]No environment variables set. Use: req env set KEY=val[/]")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    for k, v in data.items():
        display = v[:60] + "..." if len(v) > 60 else v
        table.add_row(k, display)

    console.print()
    console.print(table)
    console.print(f"[dim]{len(data)} variable(s)[/]\n")


def load_dotenv(console: Console, path: str | None = None) -> int:
    """Import variables from a .env file into the store."""
    filepath = Path(path or ".env")
    if not filepath.exists():
        console.print(f"[red]File not found:[/] {filepath}")
        return 0

    content = filepath.read_text(encoding="utf-8-sig")
    data = _load()
    added = 0
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("\"'")
            if k not in data:
                data[k] = v
                added += 1

    _save(data)
    console.print(f"  [green]Imported {added} variable(s)[/] from {filepath}")
    return added


def export_dotenv(console: Console, path: str | None = None) -> None:
    """Export stored variables to a .env file."""
    filepath = Path(path or ".env")
    data = _load()
    if not data:
        console.print("[dim]No variables to export[/]")
        return

    lines = [f"{k}={v}" for k, v in data.items()]
    content = "\n".join(lines) + "\n"

    if filepath.exists():
        console.print(f"[yellow]{filepath} exists. Back it up first if needed.[/]")

    filepath.write_text(content, encoding="utf-8")
    console.print(f"  [green]Exported {len(data)} variable(s)[/] to {filepath}")
