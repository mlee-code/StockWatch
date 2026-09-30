"""Registra no metadata as métricas de desempenho de uma versão (DECISION-003).

Entrada: o JSON do pytest-benchmark (SUITE-DES). O script também mede, no mesmo
banco de volume, o pico de memória (tracemalloc) e os pontos quentes (cProfile) das
consultas mais pesadas, guarda o perfil como artefato e liga cada métrica à mesma
métrica da versão anterior no mesmo ambiente (baseline), com a variação relativa.

Uso, a partir da raiz do repositório e com a árvore limpa no commit medido:
    .venv/bin/python scripts/registrar_desempenho.py desempenho.json --versao 0.1.0
"""

import argparse
import cProfile
import hashlib
import io
import json
import os
import platform
import pstats
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import tracemalloc
from datetime import UTC, datetime
from importlib import metadata as pacotes
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from tests.volume.gerador import HOJE, gerar  # noqa: E402

from stockwatch.aplicacao.servico import ServicoEstoque  # noqa: E402
from stockwatch.persistencia.sqlite import BancoSqlite  # noqa: E402

METADATA = RAIZ / "metadata" / "metadata.sqlite3"
ARTEFATOS = RAIZ / "metadata" / "artefatos"
PROJETO, PESSOA = "PRJ-STOCKWATCH", "PER-001"
DEPENDENCIAS = ["textual", "hypothesis", "pytest", "pytest-benchmark"]
VOLUME = "10 mil produtos, 1 milhão de movimentações (tests/volume/gerador.py)"


def agora() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def sha256(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def commit_atual() -> str:
    sujo = subprocess.run(
        ["git", "status", "--porcelain", "--", "src"],
        capture_output=True,
        text=True,
        cwd=RAIZ,
        check=True,
    ).stdout.strip()
    if sujo:
        sys.exit("src/ tem alterações sem commit: a medição não corresponderia a um commit.")
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=RAIZ, check=True
    ).stdout.strip()


def ambiente() -> dict[str, str]:
    """Descrição sanitizada da máquina; o fingerprint identifica medições comparáveis."""
    cpu = next(
        (
            linha.split(":", 1)[1].strip()
            for linha in Path("/proc/cpuinfo").read_text().splitlines()
            if linha.startswith("model name")
        ),
        platform.processor() or "desconhecido",
    )
    memoria_kb = next(
        (
            int(linha.split()[1])
            for linha in Path("/proc/meminfo").read_text().splitlines()
            if linha.startswith("MemTotal")
        ),
        0,
    )
    hardware = json.dumps(
        {"cpu": cpu, "nucleos": os.cpu_count(), "memoria_gb": round(memoria_kb / 1024**2, 1)},
        sort_keys=True,
    )
    runtime = json.dumps(
        {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version}, sort_keys=True
    )
    dependencias = json.dumps(
        {nome: pacotes.version(nome) for nome in DEPENDENCIAS}, sort_keys=True
    )
    sistema = f"{platform.system()} {platform.release()}"
    impressao = sha256("|".join([hardware, runtime, dependencias, sistema]).encode())
    return {
        "hardware": hardware,
        "runtime": runtime,
        "dependencias": dependencias,
        "sistema": sistema,
        "impressao": impressao,
    }


def medir_memoria_e_perfil(versao: str) -> tuple[dict[str, float], bytes]:
    """Pico de memória por consulta (tracemalloc) e perfil cProfile das consultas pesadas."""
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "volume.db"
        gerar(caminho)
        banco = BancoSqlite(caminho)
        servico = ServicoEstoque(banco.nova_unidade, hoje=lambda: HOJE)
        picos = {}
        for consulta in ["painel", "validades", "estoque_atual", "listar_produtos"]:
            tracemalloc.start()
            getattr(servico, consulta)()
            picos[consulta] = tracemalloc.get_traced_memory()[1] / 1024**2
            tracemalloc.stop()
        perfil = cProfile.Profile()
        perfil.enable()
        servico.painel()
        servico.validades()
        perfil.disable()
        banco.fechar()
    saida = io.StringIO()
    saida.write(f"StockWatch {versao}: cProfile de painel() + validades() com {VOLUME}\n\n")
    pstats.Stats(perfil, stream=saida).sort_stats("cumulative").print_stats(30)
    return picos, saida.getvalue().encode()


def percentil(dados: list[float], p: int) -> float:
    return statistics.quantiles(dados, n=100, method="inclusive")[p - 1]


def registrar(conexao: sqlite3.Connection, json_benchmark: Path, versao: str) -> None:
    commit = commit_atual()
    instante = agora()
    versao_id, ciclo_id = f"VER-{versao}", "CYC-001"
    conexao.execute(
        "INSERT OR IGNORE INTO versions VALUES (?, ?, ?, ?, ?)",
        (versao_id, PROJETO, versao, commit, instante),
    )
    conexao.execute(
        """INSERT OR IGNORE INTO development_cycles
           (cycle_id, version_id, cycle_type, objective, started_at, created_by_person_id)
           VALUES (?, ?, 'feature', ?, '2026-09-28T00:00:00+00:00', ?)""",
        (ciclo_id, versao_id, "Primeira versão utilizável do StockWatch (PROP-001).", PESSOA),
    )
    amb = ambiente()
    ambiente_id = "ENV-" + amb["impressao"][:12]
    conexao.execute(
        "INSERT OR IGNORE INTO environments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            ambiente_id,
            "estação do responsável",
            amb["impressao"],
            amb["hardware"],
            amb["sistema"],
            amb["runtime"],
            amb["dependencias"],
            "{}",
            instante,
        ),
    )
    grupo_id = f"TRG-DES-{versao}-{instante[:19].replace(':', '')}"
    conexao.execute(
        "INSERT INTO test_run_groups VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            grupo_id,
            ciclo_id,
            "SUITE-DES: benchmarks e profiling (DECISION-003)",
            instante,
            instante,
            "Métricas registradas; comparação com a versão anterior pela baseline.",
            "Uma máquina; medições de outro ambiente não são comparáveis.",
        ),
    )
    dados = json.loads(json_benchmark.read_text())
    for bench in dados["benchmarks"]:
        nome = bench["name"]
        definicao_id = f"TDEF-DES-{nome}"
        conexao.execute(
            """INSERT OR IGNORE INTO test_definitions
               (test_definition_id, project_id, external_id, test_type, title, source_document,
                source_revision, requirement_reference, created_at)
               VALUES (?, ?, ?, 'performance', ?, 'docs/testing/TESTS.md', ?, 'NFR-003', ?)""",
            (definicao_id, PROJETO, nome, bench["fullname"], commit, instante),
        )
        execucao_id = f"TRUN-{grupo_id[4:]}-{nome}"
        tempos = [t * 1000 for t in bench["stats"]["data"]]
        conexao.execute(
            """INSERT INTO test_runs (test_run_id, run_group_id, test_definition_id,
               environment_id, attempt_number, status, started_at, completed_at, duration_ms,
               method, load_description, dataset_reference, executed_by_person_id)
               VALUES (?, ?, ?, ?, 1, 'passed', ?, ?, ?, 'pytest-benchmark', ?, ?, ?)""",
            (
                execucao_id,
                grupo_id,
                definicao_id,
                ambiente_id,
                instante,
                instante,
                sum(tempos),
                f"{len(tempos)} rodadas",
                VOLUME,
                PESSOA,
            ),
        )
        metrica = "tempo_por_operacao"
        anterior = conexao.execute(
            """SELECT pm.metric_id, pm.p95_value FROM performance_metrics pm
               JOIN test_runs tr ON tr.test_run_id = pm.test_run_id
               JOIN test_run_groups g ON g.run_group_id = tr.run_group_id
               WHERE tr.test_definition_id = ? AND tr.environment_id = ?
                 AND pm.metric_name = ? AND g.run_group_id <> ?
               ORDER BY pm.created_at DESC LIMIT 1""",
            (definicao_id, ambiente_id, metrica, grupo_id),
        ).fetchone()
        p95 = percentil(tempos, 95)
        conexao.execute(
            """INSERT INTO performance_metrics (metric_id, test_run_id, metric_name, unit,
               sample_count, mean_value, median_value, standard_deviation, p50_value,
               p95_value, p99_value, minimum_value, maximum_value, baseline_metric_id,
               relative_change, algorithm_parameters_json, created_at)
               VALUES (?, ?, ?, 'ms', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                f"MET-{execucao_id[5:]}",
                execucao_id,
                metrica,
                len(tempos),
                statistics.mean(tempos),
                statistics.median(tempos),
                statistics.stdev(tempos),
                percentil(tempos, 50),
                p95,
                percentil(tempos, 99),
                min(tempos),
                max(tempos),
                anterior[0] if anterior else None,
                (p95 - anterior[1]) / anterior[1] if anterior else None,
                json.dumps({"rodadas": len(tempos)}),
                instante,
            ),
        )
    picos, perfil = medir_memoria_e_perfil(versao)
    execucao_memoria = f"TRUN-{grupo_id[4:]}-memoria"
    conexao.execute(
        """INSERT INTO test_runs (test_run_id, run_group_id, environment_id, attempt_number,
           status, started_at, completed_at, method, load_description, dataset_reference,
           executed_by_person_id)
           VALUES (?, ?, ?, 1, 'passed', ?, ?, 'tracemalloc + cProfile', ?, ?, ?)""",
        (
            execucao_memoria,
            grupo_id,
            ambiente_id,
            instante,
            instante,
            "uma execução de cada consulta",
            VOLUME,
            PESSOA,
        ),
    )
    for consulta, pico in picos.items():
        conexao.execute(
            "INSERT INTO resource_measurements VALUES (?, ?, ?, ?, 'MiB', 'pico', ?)",
            (
                f"RES-{execucao_memoria[5:]}-{consulta}",
                execucao_memoria,
                f"memoria_python:{consulta}",
                pico,
                instante,
            ),
        )
    ARTEFATOS.mkdir(parents=True, exist_ok=True)
    arquivo = ARTEFATOS / f"perfil-{versao}.txt"
    arquivo.write_bytes(perfil)
    conexao.execute(
        """INSERT INTO artifacts (artifact_id, cycle_id, test_run_id, artifact_type, uri,
           sha256, media_type, sensitivity, created_at)
           VALUES (?, ?, ?, 'profile', ?, ?, 'text/plain', 'public', ?)""",
        (
            f"ART-perfil-{versao}",
            ciclo_id,
            execucao_memoria,
            str(arquivo.relative_to(RAIZ)),
            sha256(perfil),
            instante,
        ),
    )


def main() -> None:
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    leitor.add_argument("json_benchmark", type=Path)
    leitor.add_argument("--versao", required=True)
    leitor.add_argument("--metadata", type=Path, default=METADATA, help="para ensaios numa cópia")
    opcoes = leitor.parse_args()
    conexao = sqlite3.connect(opcoes.metadata, isolation_level=None)
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.execute("BEGIN")
    try:
        registrar(conexao, opcoes.json_benchmark, opcoes.versao)
        if conexao.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("chaves estrangeiras inconsistentes")
        conexao.execute("COMMIT")
    except BaseException:
        conexao.execute("ROLLBACK")
        raise
    finally:
        conexao.close()
    print("Métricas registradas em", opcoes.metadata)


if __name__ == "__main__":
    main()
