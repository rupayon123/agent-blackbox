from __future__ import annotations

import json

from agent_blackbox.cli import main
from agent_blackbox.ledger import Ledger


def _seed(db_path):
    led = Ledger(str(db_path))
    led.record("agent-a", "sql_query", target="warehouse.orders")
    led.record("agent-b", "tool_call", target="browser")
    led.record("agent-a", "file_read", target="README.md")
    led.close()


def test_tail_filters_by_actor(tmp_path, capsys):
    db_path = tmp_path / "ledger.db"
    _seed(db_path)

    assert main(["tail", "--db", str(db_path), "--actor", "agent-a", "-n", "5"]) == 0

    out = capsys.readouterr().out
    assert "agent-a sql_query warehouse.orders" in out
    assert "agent-a file_read README.md" in out
    assert "agent-b tool_call browser" not in out


def test_export_jsonl_filters_by_action(tmp_path, capsys):
    db_path = tmp_path / "ledger.db"
    _seed(db_path)

    assert main(["export", "--db", str(db_path), "--action", "tool_call"]) == 0

    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["actor"] == "agent-b"
    assert row["action"] == "tool_call"
    assert row["target"] == "browser"
