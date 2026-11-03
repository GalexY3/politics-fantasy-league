"""run_demo.py is a fixed-loopback launcher, not a network host selector."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import run_demo


SCRIPT = Path(run_demo.__file__).resolve()


def test_default_launcher_keeps_exact_db_and_port(monkeypatch):
    calls = []
    monkeypatch.setattr(run_demo, 'serve', lambda db, *, port: calls.append((db, port)))

    run_demo.main([])

    assert calls == [(run_demo.ROOT / 'data' / 'demo' / 'game.db', 8787)]


@pytest.mark.parametrize('port', ['0', '1', '65535'])
def test_valid_port_and_custom_db_are_forwarded_without_server(monkeypatch, tmp_path, port):
    calls = []
    monkeypatch.setattr(run_demo, 'serve', lambda db, *, port: calls.append((db, port)))
    custom_db = tmp_path / 'unused' / 'game.db'

    run_demo.main(['--port', port, '--db', str(custom_db)])

    assert calls == [(custom_db, int(port))]
    assert not custom_db.exists()


@pytest.mark.parametrize('port', ['-1', '65536', 'abc', '1.5'])
def test_invalid_port_exits_before_starting_server(monkeypatch, port):
    calls = []
    monkeypatch.setattr(run_demo, 'serve', lambda db, *, port: calls.append((db, port)))

    with pytest.raises(SystemExit) as exc:
        run_demo.main(['--port', port])

    assert exc.value.code == 2
    assert calls == []


def test_help_subprocess_does_not_create_database(tmp_path):
    unused_db = tmp_path / 'not-created.sqlite3'
    result = subprocess.run([sys.executable, str(SCRIPT), '--db', str(unused_db), '--help'],
                            cwd=tmp_path, text=True, capture_output=True,
                            timeout=10, check=False)
    assert result.returncode == 0
    assert '--port' in result.stdout and '--db' in result.stdout
    assert '--host' not in result.stdout
    assert not unused_db.exists()


def test_invalid_port_subprocess_returns_nonzero_without_database(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT), '--port', '65536',
                             '--db', str(tmp_path / 'not-created.db')],
                            cwd=tmp_path, text=True, capture_output=True,
                            timeout=10, check=False)
    assert result.returncode != 0
    assert '0 y 65535' in result.stderr
    assert not (tmp_path / 'not-created.db').exists()


def test_public_host_option_is_not_exposed(monkeypatch):
    monkeypatch.setattr(run_demo, 'serve', lambda *args, **kwargs: pytest.fail('serve called'))
    with pytest.raises(SystemExit) as exc:
        run_demo.main(['--host', '0.0.0.0'])
    assert exc.value.code == 2
