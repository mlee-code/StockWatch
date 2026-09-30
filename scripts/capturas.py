"""Gera as capturas de tela do README (SVG) com dados de exemplo fixos.

Uso: .venv/bin/python scripts/capturas.py
"""

import asyncio
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from stockwatch.aplicacao.servico import ServicoEstoque  # noqa: E402
from stockwatch.dominio.estoque import MotivoSaida  # noqa: E402
from stockwatch.persistencia.sqlite import BancoSqlite  # noqa: E402
from stockwatch.tui.app import StockWatchApp  # noqa: E402

HOJE = date(2026, 10, 1)
DESTINO = RAIZ / "docs" / "imagens"


def popular(servico: ServicoEstoque) -> None:
    produtos = [
        ("Leite integral 1 L", "Laticínios"),
        ("Iogurte natural", "Laticínios"),
        ("Pão de forma", "Padaria"),
        ("Arroz 5 kg", "Grãos"),
        ("Feijão carioca 1 kg", "Grãos"),
        ("Detergente 500 ml", "Limpeza"),
    ]
    for nome, categoria in produtos:
        servico.cadastrar_produto(nome, categoria)
    entradas = [
        ("Leite integral 1 L", 24, date(2026, 9, 29), "Laticínios Sul"),
        ("Leite integral 1 L", 36, date(2026, 10, 12), "Laticínios Sul"),
        ("Iogurte natural", 12, date(2026, 10, 3), "Laticínios Sul"),
        ("Pão de forma", 10, date(2026, 10, 1), "Padaria Central"),
        ("Arroz 5 kg", 20, date(2027, 8, 1), None),
        ("Feijão carioca 1 kg", 30, date(2027, 3, 15), None),
        ("Detergente 500 ml", 40, None, None),
    ]
    for produto, quantidade, validade, fornecedor in entradas:
        servico.registrar_entrada(produto, quantidade, validade, fornecedor)
    servico.registrar_saida("Leite integral 1 L", 18, MotivoSaida.VENDA)
    servico.registrar_saida("Arroz 5 kg", 4, MotivoSaida.VENDA)


async def capturar(servico: ServicoEstoque) -> None:
    telas = {"painel": [], "produtos": ["p"], "validades": ["v"], "saida": ["s"]}
    for nome, teclas in telas.items():
        app = StockWatchApp(servico)
        async with app.run_test(size=(100, 28)) as piloto:
            for tecla in teclas:
                await piloto.press(tecla)
            if nome == "saida":
                await piloto.press("i", *"Leite integral 1 L", "tab", *"10", "enter")
            await piloto.pause()
            app.save_screenshot(filename=f"{nome}.svg", path=str(DESTINO))


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    banco = BancoSqlite(Path(":memory:"))
    servico = ServicoEstoque(banco.nova_unidade, hoje=lambda: HOJE)
    popular(servico)
    asyncio.run(capturar(servico))
    banco.fechar()
    print("Capturas em", DESTINO.relative_to(RAIZ))


if __name__ == "__main__":
    main()
