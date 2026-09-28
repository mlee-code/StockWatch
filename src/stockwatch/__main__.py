"""Executa a TUI: `python -m stockwatch` ou `stockwatch`."""

from stockwatch.tui.app import StockWatchApp


def main() -> None:
    StockWatchApp().run()


if __name__ == "__main__":
    main()
