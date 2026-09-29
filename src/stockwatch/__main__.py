"""Executa a TUI: `python -m stockwatch` ou `stockwatch`."""

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.persistencia.sqlite import BancoSqlite
from stockwatch.tui.app import StockWatchApp


def caminho_do_banco(argumentos: Sequence[str]) -> Path:
    """Arquivo do banco: `--banco` ou `$XDG_DATA_HOME/stockwatch/stockwatch.db` (REQ-010)."""
    leitor = argparse.ArgumentParser(
        prog="stockwatch", description="Controle de estoque e validade no terminal."
    )
    leitor.add_argument("--banco", type=Path, metavar="CAMINHO", help="arquivo SQLite a usar")
    opcoes = leitor.parse_args(argumentos)
    if opcoes.banco is not None:
        return Path(opcoes.banco)
    dados = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local/share")
    return Path(dados) / "stockwatch" / "stockwatch.db"


def main(argumentos: Sequence[str] | None = None) -> None:
    """Raiz de composição: monta persistência, serviço e TUI."""
    banco = BancoSqlite(caminho_do_banco(sys.argv[1:] if argumentos is None else argumentos))
    try:
        StockWatchApp(ServicoEstoque(banco.nova_unidade)).run()
    finally:
        banco.fechar()


if __name__ == "__main__":
    main()
