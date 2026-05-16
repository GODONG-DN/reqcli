"""Tests for environment variable manager."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from req import env as env_mod


class TestEnv:
    def test_save_and_load(self, tmp_path: Path):
        env_path = tmp_path / "env.json"
        with patch.object(env_mod, "ENV_FILE", env_path):
            env_mod._save({"KEY": "val"})
            assert env_mod._load() == {"KEY": "val"}

    def test_substitute_replaces_vars(self, tmp_path: Path):
        env_path = tmp_path / "env.json"
        env_path.write_text(json.dumps({"BASE": "https://api.example.com", "TOKEN": "abc"}))

        with patch.object(env_mod, "ENV_FILE", env_path):
            result = env_mod.substitute("{{BASE}}/users?token={{TOKEN}}")
            assert result == "https://api.example.com/users?token=abc"

    def test_substitute_no_file(self, tmp_path: Path):
        env_path = tmp_path / "nonexistent.json"
        with patch.object(env_mod, "ENV_FILE", env_path):
            result = env_mod.substitute("https://example.com")
            assert result == "https://example.com"

    def test_set_and_get(self, tmp_path: Path):
        env_path = tmp_path / "env.json"
        console = Console()

        with patch.object(env_mod, "ENV_FILE", env_path):
            env_mod.set_var(console, "TOKEN", "secret")
            assert env_mod._load()["TOKEN"] == "secret"

    def test_delete_var(self, tmp_path: Path):
        env_path = tmp_path / "env.json"
        env_path.write_text(json.dumps({"TOKEN": "secret", "URL": "http://x.com"}))

        with patch.object(env_mod, "ENV_FILE", env_path):
            console = Console()
            env_mod.delete_var(console, "TOKEN")
            data = env_mod._load()
            assert "TOKEN" not in data
            assert data["URL"] == "http://x.com"
