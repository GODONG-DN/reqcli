"""Tests for request collection."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from req import collection as coll_mod
from req.collection import COLLECTION_FILE


class TestCollection:
    def test_init_collection(self, tmp_path: Path):
        path = tmp_path / "collection.json"
        console = Console()

        with patch.object(coll_mod, "COLLECTION_FILE", path):
            coll_mod.init_collection(console, "test")
            data = json.loads(path.read_text())
            assert data["name"] == "test"
            assert data["requests"] == []

    def test_add_and_list(self, tmp_path: Path):
        path = tmp_path / "collection.json"
        console = Console()

        with patch.object(coll_mod, "COLLECTION_FILE", path):
            coll_mod.init_collection(console, "test")
            coll_mod.add_request(
                console, "Get Users", "GET", "/users",
                headers=["Authorization: Bearer xyz"],
            )
            coll_mod.add_request(
                console, "Create", "POST", "/users",
                json_body='{"name":"John"}',
            )

            data = json.loads(path.read_text())
            assert len(data["requests"]) == 2
            assert data["requests"][0]["method"] == "GET"
            assert data["requests"][1]["method"] == "POST"
            assert data["requests"][1]["body"] == {"name": "John"}
