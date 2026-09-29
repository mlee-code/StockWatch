"""SUITE-UNIT: raiz de composição e local do banco (REQ-010 CA-3)."""

from pathlib import Path

import pytest

from stockwatch.__main__ import caminho_do_banco


def test_usa_xdg_data_home_quando_definido(monkeypatch: pytest.MonkeyPatch) -> None:
    """TEST-UNIT-020: padrão em $XDG_DATA_HOME/stockwatch/stockwatch.db."""
    monkeypatch.setenv("XDG_DATA_HOME", "/dados")
    assert caminho_do_banco([]) == Path("/dados/stockwatch/stockwatch.db")


def test_usa_local_share_sem_xdg(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """TEST-UNIT-021: sem XDG_DATA_HOME, usa ~/.local/share (especificação XDG)."""
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert caminho_do_banco([]) == tmp_path / ".local/share/stockwatch/stockwatch.db"


def test_opcao_banco_substitui_o_padrao() -> None:
    """TEST-UNIT-022: --banco CAMINHO escolhe outro arquivo."""
    assert caminho_do_banco(["--banco", "/tmp/loja.db"]) == Path("/tmp/loja.db")
