"""Gera docs/CHANGELOG.md a partir dos commits convencionais (projeção do histórico do Git).

Uso: .venv/bin/python scripts/changelog.py 0.1.0 [--desde REF]
"""

import argparse
import re
import subprocess
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SECOES = {
    "feat": "Funcionalidades",
    "fix": "Correções",
    "perf": "Desempenho",
    "refactor": "Refatorações",
}
PADRAO = re.compile(r"^(?P<tipo>\w+)(\([^)]*\))?(?P<quebra>!)?: (?P<descricao>.+)$")


def commits(desde: str | None) -> list[str]:
    intervalo = f"{desde}..HEAD" if desde else "HEAD"
    saida = subprocess.run(
        ["git", "log", "--no-merges", "--reverse", "--format=%s", intervalo],
        capture_output=True,
        text=True,
        cwd=RAIZ,
        check=True,
    )
    return saida.stdout.splitlines()


def gerar(versao: str, desde: str | None) -> str:
    grupos: dict[str, list[str]] = {tipo: [] for tipo in SECOES}
    for assunto in commits(desde):
        if (casamento := PADRAO.match(assunto)) and casamento["tipo"] in grupos:
            grupos[casamento["tipo"]].append(casamento["descricao"])
    linhas = [
        "# CHANGELOG",
        "",
        "Gerado por `scripts/changelog.py` a partir dos commits convencionais; não editar à mão.",
        "",
        f"## {versao} — {date.today().isoformat()}",
    ]
    for tipo, titulo in SECOES.items():
        if grupos[tipo]:
            linhas += ["", f"### {titulo}", *(f"- {item}" for item in grupos[tipo])]
    return "\n".join(linhas) + "\n"


def main() -> None:
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    leitor.add_argument("versao")
    leitor.add_argument("--desde", help="referência da versão anterior (tag ou commit)")
    opcoes = leitor.parse_args()
    destino = RAIZ / "docs" / "CHANGELOG.md"
    destino.write_text(gerar(opcoes.versao, opcoes.desde), encoding="utf-8")
    print("Gerado", destino.relative_to(RAIZ))


if __name__ == "__main__":
    main()
