"""Executa a TUI: `python -m stockwatch` ou `stockwatch`."""

from pathlib import Path

from stockwatch.aplicacao.servico import ServicoEstoque
from stockwatch.persistencia.sqlite import BancoSqlite
from stockwatch.tui.app import StockWatchApp


def main() -> None:
    """Raiz de composição: monta persistência, serviço e TUI."""
    banco = BancoSqlite(Path.home() / ".local/share/stockwatch/stockwatch.db")
    try:
        StockWatchApp(ServicoEstoque(banco.nova_unidade)).run()
    finally:
        banco.fechar()


if __name__ == "__main__":
    main()
