"""AB10 P03: real local MemPalace vs strong SQLite FTS on IDENTICAL toy docs.

The fixtures are completely invented. Neither private conversations nor real
PAN/IAEN rows are read. Results do not prove general model capability.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys


SCHEMA = "pfl.ab10.mempalace_semantic_synthetic.v1"
WING = "ab10-synthetic-current"
CASE_DATA = (
    ("FAUNO",
     "El almacenamiento de tablas analíticas de este proyecto ficticio reside en DuckDB. La base relacional permite cálculos locales sin compartir ningún archivo personal.",
     "Las tablas vivían anteriormente en SQLite, pero esa arquitectura fue sustituida en la edición actual.",
     "¿Qué motor sirve para guardar y consultar tablas analíticas?"),
    ("COBALTO",
     "La cronología institucional separa momento del acontecimiento, fecha de publicidad y fecha de captura. Ninguna de estas tres marcas es intercambiable con otra.",
     "Antes solo existía una marca temporal sin distinguir evento, anuncio ni adquisición.",
     "¿Cómo evitar confundir cuándo sucedió algo con cuándo fue conocido públicamente?"),
    ("ESTRIBO",
     "Una actuación cuyo desenlace no se ha observado permanece en estado pendiente o censurado. La ausencia de resolución no prueba rechazo institucional.",
     "La clasificación anterior transformaba automáticamente cualquier ausencia en decisión negativa.",
     "¿Qué etiqueta corresponde a un expediente sin resultado final conocido?"),
    ("VELERO",
     "La identidad de dos iniciativas exige un identificador documental acreditado. La semejanza literal de sus títulos solo permite formular una hipótesis de enlace.",
     "El esquema obsoleto unía automáticamente dos iniciativas con nombres parecidos.",
     "¿Basta que dos proyectos se llamen igual para afirmar que son el mismo objeto?"),
    ("NAVEGA",
     "Los originales con restricciones se conservan fuera del árbol Git en un almacén privado y las derivadas solo se divulgan si los derechos concretos lo permiten.",
     "Antes todos los ficheros originales se copiaban al repositorio de demostración.",
     "¿Dónde debemos conservar documentos fuente que no pueden redistribuirse?"),
    ("DORADO",
     "Cada distribución oficial requiere una comprobación específica de condiciones de reutilización, atribución y límites de la licencia antes de hacerla pública.",
     "La antigua política asumía reutilización ilimitada por tratarse de un sitio público.",
     "¿Qué condiciones jurídicas hay que comprobar antes de publicar una fuente oficial?"),
    ("CIERZO",
     "Una red de contagio inventada permite estudiar lo que se deduce de reglas impuestas, pero no constituye evidencia causal sobre figuras políticas verdaderas.",
     "El antiguo informe presentaba las activaciones del juguete como influencia social observada.",
     "¿Una simulación de difusión prueba influencia política en personas reales?"),
    ("LIRA",
     "La aceptación del recorrido de dos cuentas requiere evaluación humana del uso real. Los tests HTTP o de interfaz automatizada son evidencia de funcionamiento parcial.",
     "Antes la herramienta se consideraba aceptada al completar únicamente una prueba HTTP.",
     "¿Puede un test automático aprobar por sí mismo una experiencia entre cuentas?"),
    ("ONICE",
     "Una norma adoptada en 2025 no puede ser una aprobación conocida al corte 31 de diciembre de 2024 por figurar después en un informe retrospectivo.",
     "La clasificación anterior atribuía al año 2024 todas las aprobaciones relatadas por el informe posterior.",
     "¿Cómo impedimos usar decisiones del año siguiente para predecir el anterior?"),
    ("TORRE",
     "Un inventario GitHub comprueba las ramas de solicitud de cambios abiertas, compara sus cabezas remotas y alerta cuando dos líneas paralelas editan el mismo contrato.",
     "Antes solo se revisaban tres ramas nombradas manualmente y las demás podían quedar invisibles.",
     "¿Cómo detectar solicitudes de cambio paralelas que chocan en los mismos archivos?"),
)


class MemBenchmarkError(RuntimeError):
    pass


def docs() -> tuple[dict, ...]:
    if len(CASE_DATA) != 10 or len({x[0] for x in CASE_DATA}) != 10:
        raise MemBenchmarkError("TEN_DISTINCT_SYNTHETIC_CASES_REQUIRED")
    records = []
    for n, (label, current, historical, question) in enumerate(CASE_DATA, 1):
        if not all(type(x) is str and 20 <= len(x) <= 850 for x in (current, historical, question)):
            raise MemBenchmarkError("CASE_TEXT_UNTRUSTED")
        if label.casefold() in question.casefold():
            raise MemBenchmarkError("QUESTION_CONTAINS_SYNTHETIC_PROJECT_ID")
        name = f"syn-{n:02d}.md"
        records.append({
            "id": n, "file": name, "query": question,
            "current_content": (f"# PROYECTO FICTICIO {label} - DECISION ACTUAL\n"
                                f"Este documento es totalmente sintético. {current}\n"),
            "historical_content": (f"# PROYECTO FICTICIO {label} - VERSION RETIRADA\n"
                                   f"Antecedente de juguete, no vigente: {historical}\n"),
        })
    return tuple(records)


def ensure_off_git(root: Path) -> Path:
    p = root.resolve()
    if not p.is_dir() or (p / "current").exists() or (p / "historical").exists():
        raise MemBenchmarkError("NEW_EMPTY_OFFGIT_ROOT_REQUIRED")
    if any((parent / ".git").exists() for parent in (p, *p.parents)):
        raise MemBenchmarkError("SYNTHETIC_OUTPUT_INSIDE_GIT_CHECKOUT")
    return p


def create_files(root: Path, corpus: tuple[dict, ...]) -> dict[str, str]:
    a = root / "current"
    b = root / "historical"
    a.mkdir()
    b.mkdir()
    receipt = {}
    for case in corpus:
        for target, field in ((a, "current_content"), (b, "historical_content")):
            out = target / case["file"]
            data = case[field].encode("utf-8")
            with out.open("xb") as f:
                f.write(data)
            receipt[f"{target.name}/{case['file']}"] = sha256(data).hexdigest()
    return receipt


def tokenize(query: str) -> str:
    blacklist = {"cual", "como", "donde", "cuando", "puede", "para",
                 "antes", "despues", "sobre", "cada", "deben"}
    terms = [
        x.casefold() for x in re.findall(r"[^\W_]+", query, flags=re.UNICODE)
        if len(x) >= 4 and x.casefold() not in blacklist
    ]
    if not terms:
        raise MemBenchmarkError("FTS_EMPTY_QUERY")
    return " OR ".join('"' + word.replace('"', "") + '"' for word in dict.fromkeys(terms))


def fts_search(corpus: tuple[dict, ...], query: str, k: int = 3) -> tuple[str, ...]:
    """Strong version-scoped BM25: ONLY current docs, not historical ones."""
    if type(k) is not int or k != 3:
        raise MemBenchmarkError("TOPK_MUST_BE_EQUAL")
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE VIRTUAL TABLE archive USING fts5(file UNINDEXED, content, tokenize='unicode61 remove_diacritics 2')")
        con.executemany("INSERT INTO archive(file,content) VALUES(?,?)",
                        [(x["file"], x["current_content"]) for x in corpus])
        hits = con.execute(
            "SELECT file FROM archive WHERE archive MATCH ? ORDER BY bm25(archive) LIMIT ?",
            (tokenize(query), k),
        ).fetchall()
        return tuple(h[0] for h in hits)
    finally:
        con.close()


def parse_mempalace_sources(output: str, *, allowed: set[str], k: int = 3) -> tuple[str, ...]:
    if type(output) is not str or len(output) > 90_000:
        raise MemBenchmarkError("SEMANTIC_CLI_OUTPUT_INVALID")
    candidates = re.findall(r"(?m)^\s*Source:\s*(syn-\d{2}\.md)\s*$", output)
    seen = set()
    result = []
    for candidate in candidates:
        if candidate not in allowed:
            raise MemBenchmarkError("SEMANTIC_SOURCE_NOT_IN_CURRENT_CORPUS")
        if candidate not in seen:
            seen.add(candidate)
            result.append(candidate)
    if not result or len(result) > k:
        raise MemBenchmarkError("SEMANTIC_CLI_NO_VALID_TOPK")
    return tuple(result)


def environ_for_mempalace(lab: Path, palace: Path) -> dict[str, str]:
    exe = lab / ".venv" / "Scripts" / "mempalace.exe"
    model_cache = lab / "cache" / "huggingface"
    if not exe.is_file() or not model_cache.exists():
        raise MemBenchmarkError("MEMPALACE_NOT_INSTALLED_OR_MODEL_CACHE_MISSING")
    env = os.environ.copy()
    env.update({
        "HOME": str(lab / "home"), "USERPROFILE": str(lab / "home"),
        "XDG_CACHE_HOME": str(lab / "cache"), "HF_HOME": str(model_cache),
        "MEMPALACE_PALACE_PATH": str(palace),
        "MEMPALACE_EMBEDDING_MODEL": "embeddinggemma",
        "MEMPALACE_EMBEDDING_DEVICE": "cpu", "HF_HUB_OFFLINE": "1",
        "HF_HUB_DISABLE_TELEMETRY": "1", "DO_NOT_TRACK": "1",
        "ANONYMIZED_TELEMETRY": "False", "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "", "PYTHONUTF8": "1",
    })
    return env


def run_cli(args: list[str], env: dict[str, str], cwd: Path, timeout: int = 150) -> str:
    proc = subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          shell=False, timeout=timeout)
    if proc.returncode:
        raise MemBenchmarkError(f"MEMPALACE_CLI_EXIT_{proc.returncode}")
    return proc.stdout


def evaluate(root: Path, lab: Path) -> dict:
    root = ensure_off_git(root)
    corpus = docs()
    receipts = create_files(root, corpus)
    env = environ_for_mempalace(lab, root / "palace")
    exe = str(lab / ".venv" / "Scripts" / "mempalace.exe")
    run_cli([exe, "mine", str(root / "current"), "--wing", WING, "--direct",
             "--max-chunks-per-file", "8"], env, root, timeout=180)
    allowed = {c["file"] for c in corpus}
    answers = []
    for case in corpus:
        try:
            semantic_raw = run_cli([exe, "search", case["query"], "--wing", WING,
                                     "--results", "3"], env, root)
            semantic = parse_mempalace_sources(semantic_raw, allowed=allowed)
        except (MemBenchmarkError, subprocess.TimeoutExpired):
            # Do not turn an inaccessible real model into fabricated results.
            raise
        lexical = fts_search(corpus, case["query"])
        answers.append({
            "case": case["id"], "expected": case["file"],
            "mempalace_top3": list(semantic),
            "fts_bm25_top3": list(lexical),
            "mempalace_top1_hit": bool(semantic and semantic[0] == case["file"]),
            "fts_top1_hit": bool(lexical and lexical[0] == case["file"]),
            "mempalace_top3_hit": case["file"] in semantic,
            "fts_top3_hit": case["file"] in lexical,
        })
    sem_top1 = sum(x["mempalace_top1_hit"] for x in answers)
    fts_top1 = sum(x["fts_top1_hit"] for x in answers)
    conclusion = {
        "schema": SCHEMA,
        "case_count": len(answers),
        "mempalace_real_cli_used": True,
        "embedding_model": "embeddinggemma_local_offline",
        "both_engines_same_current_documents": True,
        "historical_documents_excluded_both_engines": True,
        "mempalace_top1_count": sem_top1,
        "fts_bm25_top1_count": fts_top1,
        "mempalace_top3_count": sum(x["mempalace_top3_hit"] for x in answers),
        "fts_bm25_top3_count": sum(x["fts_top3_hit"] for x in answers),
        "H1_threshold_met": sem_top1 >= 8 and sem_top1 - fts_top1 >= 2,
        "source_sha256_current_and_historical_synthetic": receipts,
        "matches": answers,
        "real_Conversations_or_private_originals_indexed": False,
        "does_not_establish_long_term_memory_or_llm_efficacy": True,
        "R5": "STOP",
    }
    out = root / "P03_SYNTHETIC_BENCHMARK_RESULT.json"
    with out.open("x", encoding="utf-8") as f:
        json.dump(conclusion, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write("\n")
    return conclusion


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-output", required=True, type=Path)
    parser.add_argument("--mempalace-lab", required=True, type=Path)
    arguments = parser.parse_args()
    result = evaluate(arguments.private_output, arguments.mempalace_lab)
    print(json.dumps({key: result[key] for key in (
        "case_count", "mempalace_top1_count", "fts_bm25_top1_count",
        "mempalace_top3_count", "fts_bm25_top3_count", "H1_threshold_met",
        "R5")}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
