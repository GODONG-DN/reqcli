"""Req TUI — interactive API client in the terminal."""

from __future__ import annotations

import time

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    RichLog,
    Select,
    Static,
    TextArea,
)

from req.client import print_response, send_request
from req.env import list_vars, substitute


class RequestScreen(Screen):
    BINDINGS = [
        Binding("ctrl+r", "send_request", "Send"),
        Binding("ctrl+s", "focus_url", "URL"),
        Binding("ctrl+e", "focus_headers", "Headers"),
        Binding("ctrl+b", "focus_body", "Body"),
        Binding("ctrl+l", "clear_log", "Clear"),
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="left"):
                yield Static("[bold]Request[/]", id="req-title")
                yield Select(
                    [("GET", "GET"), ("POST", "POST"), ("PUT", "PUT"), ("PATCH", "PATCH"), ("DELETE", "DELETE")],
                    value="GET",
                    id="method-select",
                )
                yield Input(placeholder="https://api.example.com/endpoint", id="url-input")
                yield Input(placeholder="Authorization: Bearer token (one per line)", id="headers-input")
                yield TextArea.code_editor("", id="body-input", language="json")
                yield Button("Send [Ctrl+R]", variant="success", id="send-btn")
            with Vertical(id="right"):
                yield Static("[bold]Response[/]", id="resp-title")
                yield RichLog(id="response-log", highlight=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#url-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send-btn":
            self.action_send_request()

    def action_send_request(self) -> None:
        url_input = self.query_one("#url-input", Input)
        method_select = self.query_one("#method-select", Select)
        headers_input = self.query_one("#headers-input", Input)
        body_input = self.query_one("#body-input", TextArea)
        log = self.query_one("#response-log", RichLog)

        url = substitute(url_input.value.strip())
        if not url:
            log.write("[red]Enter a URL first[/]")
            return

        method = method_select.value or "GET"

        headers: dict[str, str] = {}
        for line in headers_input.value.strip().split("\n"):
            line = line.strip()
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip()] = v.strip()

        json_body = None
        body_text = body_input.text.strip()
        if body_text:
            import json
            try:
                json_body = json.loads(body_text)
            except json.JSONDecodeError:
                json_body = body_text

        log.clear()
        log.write(f"[bold]{method} [cyan]{url}[/][/]\n")

        start = time.time()
        try:
            resp = send_request(method, url, headers=headers, json_body=json_body)
        except Exception as exc:
            log.write(f"\n[red]Error: {exc}[/]")
            return
        elapsed = time.time() - start

        status_color = "green" if 200 <= resp.status_code < 300 else "yellow" if resp.status_code < 500 else "red"
        log.write(f"[bold {status_color}]HTTP {resp.http_version} {resp.status_code} {resp.reason_phrase}[/] [dim]{len(resp.content)} bytes in {elapsed*1000:.0f}ms[/]\n")

        if resp.headers.get("content-type", "").startswith("application/json"):
            try:
                import json
                formatted = json.dumps(json.loads(resp.text), indent=2, ensure_ascii=False)
                log.write(formatted)
            except Exception:
                log.write(resp.text[:5000])
        else:
            log.write(resp.text[:5000])

        if len(resp.text) > 5000:
            log.write(f"\n[dim]... truncated ({len(resp.content)} bytes total)[/]")

    def action_focus_url(self) -> None:
        self.query_one("#url-input", Input).focus()

    def action_focus_headers(self) -> None:
        self.query_one("#headers-input", Input).focus()

    def action_focus_body(self) -> None:
        self.query_one("#body-input", TextArea).focus()

    def action_clear_log(self) -> None:
        self.query_one("#response-log", RichLog).clear()


class ReqTUI(App):
    TITLE = "Req"
    SUB_TITLE = "Terminal API Client"

    def on_mount(self) -> None:
        self.push_screen(RequestScreen())


def run_tui() -> None:
    app = ReqTUI()
    app.run()
