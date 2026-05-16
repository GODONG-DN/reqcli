"""Tests for request state management."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from req import state as state_mod


class TestState:
    def test_set_and_get(self, tmp_path: Path):
        path = tmp_path / "state.json"
        with patch.object(state_mod, "STATE_FILE", path):
            state_mod.set_state("token", "abc123")
            assert state_mod.get_state("token") == "abc123"

    def test_substitute_state(self, tmp_path: Path):
        path = tmp_path / "state.json"
        with patch.object(state_mod, "STATE_FILE", path):
            state_mod.set_state("token", "secret")
            result = state_mod.substitute_state("Bearer {{$token}}")
            assert result == "Bearer secret"

    def test_substitute_no_match(self, tmp_path: Path):
        path = tmp_path / "state.json"
        with patch.object(state_mod, "STATE_FILE", path):
            result = state_mod.substitute_state("no vars here")
            assert result == "no vars here"

    def test_extract_from_json(self):
        body = '{"token":"abc","user":{"id":42,"name":"John"}}'
        assert state_mod.extract_value(body, "token") == "abc"
        assert state_mod.extract_value(body, "user.id") == "42"
        assert state_mod.extract_value(body, "user.name") == "John"

    def test_extract_nested_missing(self):
        body = '{"data":{"items":[1,2,3]}}'
        assert state_mod.extract_value(body, "data.items.0") == "1"
        assert state_mod.extract_value(body, "missing") == ""
        assert state_mod.extract_value(body, "data.missing") == ""
