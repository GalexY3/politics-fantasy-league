"""Build/check/search a tracked-file catalogue. Never scans local raw/private files."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT
OUTPUTS = {'PROJECT_INDEX.json', 'PROJECT_MAP.md', 'research/INDEX.md'}
CATEGORIES = {
    'continuity': 'Estado vigente, objetivos e inicio de conversación',
    'runtime': 'Aplicación, reglas y almacenamiento del prototipo',
    'experimental_code': 'Instrumentos experimentales; su presencia no prueba integración en el juego',
    'verification': 'Pruebas y ejecutores de comprobación',
    'research': 'Preguntas, campañas, análisis y resultados de investigación',
    'evidence': 'Recibos, originales conservados y copias históricas; no código activo',
    'atlas': 'Grafo Atlas, logros y sincronización',
    'atlas_engine': 'Motor Atlas fijado y sus pruebas; procedencia en UPSTREAM.json',
    'reference': 'Manuales, contratos y referencias',
    'data': 'Datos/fixtures versionados y metadatos; no datos locales privados',
    'task_queue': 'Expedientes y resultados de ejecución',
    'operations': 'Herramientas, configuración y operación local',
    'archive': 'Documentación histórica conservada',
}
ROLES = {
    'START_HERE.md': 'Inicio estable para cualquier conversación',
    'PROJECT_STATE.json': 'Autoridad del estado actual, dos líneas e hitos',
    'HANDOFF.md': 'Último briefing guardado; comprobar frescura con Git',
    'BRANCHES.json': 'Inventario de ramas integradas y alternativas históricas',
    'NEW_CHAT_PROMPT.md': 'Prompt reutilizable que apunta al estado vivo',
    'METHOD_REFERENCE.json': 'Versión de AB adoptada y enlaces al método en su repositorio',
    'src/politics_fantasy/server.py': 'Servidor HTTP de la demo local; rutas API y cabeceras',
    'src/politics_fantasy/product.py': 'Clubes, mercado, alineación, jornadas y persistencia',
    'src/politics_fantasy/scoring.py': 'Reglas de puntuación del prototipo',
    'src/politics_fantasy/web/app.js': 'Interfaz del juego y paneles',
    'src/politics_fantasy/secure_store.py': 'Almacén privado POSIX y límites de plataforma',
    'src/politics_fantasy/ingest.py': 'Captura local y controles de fuente/redirección',
    'src/politics_fantasy/quarantine_ingest.py': 'Validación y cuarentena de capturas',
    'src/politics_fantasy/private_audit.py': 'Integridad de capturas y manifiestos',
    'src/politics_fantasy/identity_reconcile.py': 'Conciliación de identidades; no adjudicación automática válida',
    'src/politics_fantasy/release_guard.cjs': 'Seis requisitos de lanzamiento; falla cerrado por defecto',
    'src/politics_fantasy/fictional_receipt_auth.mjs': 'Firma y verificación de recibos sintéticos; no autenticación de usuarios',
    'scripts/project_status.py': 'Derivar y validar estado, Atlas, presupuesto y handoff',
    'scripts/project_index.py': 'Regenerar, comprobar y buscar en la organización del proyecto',
    'scripts/run_node_tests.mjs': 'Suite Node completa, incluidos tests bajo src',
    'tareas_codex/BACKLOG.json': 'Expedientes técnicos; su alcance histórico no reemplaza el estado vivo',
    'research/ABH5B_INCENTIVE_FORMAL_20261029/O7_CAUSAL_GRAPH.json': 'Grafo O7 de preguntas y relaciones; distinto del Atlas',
}


def classify(path):
    p = PurePosixPath(path)
    parts = p.parts
    upper = path.upper()
    if path in ROLES and len(parts) == 1 or path in {'AGENTS.md', 'SESSION_LOG.jsonl'}:
        return 'continuity'
    if 'HISTORIC' in upper or path.startswith('HANDOFF_PFL_'):
        return 'archive'
    if any('EVIDENCIA' in x.upper() for x in parts) or any(x in {'originals', 'baseline', 'linux', 'windows'} for x in parts[:-1]):
        return 'evidence'
    if path.startswith('ab_atlas/'):
        return 'atlas'
    if path.startswith('tools/ab_atlas/'):
        return 'atlas_engine'
    if path.startswith('tests/') or p.name.startswith('test_') and path.startswith('src/'):
        return 'verification'
    if path.startswith('src/'):
        return 'experimental_code' if p.name.startswith(('fictional_', 'forecastbench_', 'pilot_', 'synthetic_', 'publication_asof_', 'parity_comparator_', 'vote_key_research')) else 'runtime'
    if path.startswith('research/'):
        return 'research'
    if path.startswith('tareas_codex/'):
        return 'task_queue'
    if path.startswith(('docs/', 'examples/')):
        return 'reference'
    if path.startswith('data/'):
        return 'data'
    if path.startswith('product/'):
        return 'runtime'
    return 'operations'


def make_catalogue(paths):
    records = []
    for path in sorted(set(paths)):
        p = PurePosixPath(path)
        if path in OUTPUTS or p.is_absolute() or '..' in p.parts:
            continue
        if p.parts[:2] in {('data', 'raw'), ('data', 'private'), ('data', 'local_field')}:
            continue
        category = classify(path)
        records.append({'path': path, 'category': category,
                        'purpose': ROLES.get(path, CATEGORIES[category])})
    return {'schema': 'pfl.project_index.v1', 'scope': 'Git tracked project files only; excludes local raw/private and generated indexes',
            'certifies_results': False, 'category_counts': dict(sorted(Counter(x['category'] for x in records).items())),
            'files': records}


def tracked_paths():
    prefix = '' if PROJECT == ROOT else PROJECT.relative_to(ROOT).as_posix() + '/'
    raw = subprocess.check_output(['git', 'ls-files', '-z', '--', prefix or '.'], cwd=ROOT).decode('utf-8')
    return [p[len(prefix):] for p in raw.split('\0') if p.startswith(prefix) and (ROOT / p).is_file()]


def search(catalogue, query, category=None):
    words = query.casefold().split()
    matches = [x for x in catalogue['files'] if (category is None or x['category'] == category)
               and all(w in (x['path'] + ' ' + x['purpose'] + ' ' + x['category']).casefold() for w in words)]
    def rank(row):
        score = 20 * (row['path'] in ROLES) + 10 * (row['category'] not in {'evidence','archive'})
        score += sum(5 for w in words if w in PurePosixPath(row['path']).name.casefold())
        return (-score, row['path'])
    return sorted(matches, key=rank)


def map_markdown(catalogue):
    lines = ['# Mapa de Politics Fantasy', '',
             'Mapa generado por `python scripts/project_index.py build`. El índice es navegación; **no acredita ejecución ni actualidad científica**. El estado vigente está en [PROJECT_STATE.json](PROJECT_STATE.json).', '',
             '## Dónde buscar según la tarea', '',
             '| Quiero… | Entrada |', '| --- | --- |',
             '| Continuar o empezar otro chat | [START_HERE](START_HERE.md), [prompt](NEW_CHAT_PROMPT.md) |',
             '| Saber qué falta y qué sigue | [Estado e hitos](PROJECT_STATE.json), [handoff](HANDOFF.md) |',
             '| Entender el juego local | [Servidor](src/politics_fantasy/server.py), [lógica y BD](src/politics_fantasy/product.py), [interfaz](src/politics_fantasy/web/app.js) |',
             '| Revisar datos, identidades y cuarentena | [Ingesta](src/politics_fantasy/ingest.py), [almacén](src/politics_fantasy/secure_store.py), [cuarentena](src/politics_fantasy/quarantine_ingest.py) |',
             '| Encontrar una pregunta o una campaña | [Índice de investigación](research/INDEX.md) |',
             '| Encontrar tests y comandos de QA | [Tests](tests/), [runner Node](scripts/run_node_tests.mjs), [pyproject](pyproject.toml) |',
             '| Distinguir los tres mapas | [Atlas](ab_atlas/README.md), [O7](research/ABH5B_INCENTIVE_FORMAL_20261029/O7_CAUSAL_GRAPH.json), [logros](ab_atlas/ACHIEVEMENTS_README.md) |',
             '| Localizar un expediente Txxx | [Cola](tareas_codex/README.md), [backlog](tareas_codex/BACKLOG.json) |',
             '| Saber qué rama contiene el trabajo | [Ramas](BRANCHES.json) |',
             '| Revisar la incorporación a main | [Revisión del código](docs/MAIN_REVIEW_20261030.md), [integración](research/INTEGRATION_20261030/REPORT.md) |', '',
             '## Buscar sin leer todo el historial', '',
             '```sh', 'python scripts/project_index.py find T005', 'python scripts/project_index.py find recibos',
             'python scripts/project_index.py find forecastbench --category experimental_code',
             'python scripts/project_index.py check', '```', '',
             'El catálogo completo está en [PROJECT_INDEX.json](PROJECT_INDEX.json). Solo lista archivos versionados; no explora carpetas privadas locales.', '',
             '## Responsabilidad de las carpetas', '', '| Categoría | Archivos | Uso |', '| --- | ---: | --- |']
    for category, count in catalogue['category_counts'].items():
        lines.append(f'| `{category}` | {count} | {CATEGORIES[category]} |')
    lines += ['', '## Dónde guardar trabajo nuevo', '',
              '- Funcionalidad activa en `src/politics_fantasy/`; pruebas ejecutables en `tests/`. Los módulos experimentales se identifican en el catálogo y no se consideran conectados a la app por estar en src.',
              '- Manuales mantenidos en `docs/`; decisiones e hitos actuales en `PROJECT_STATE.json`. Evitar duplicar el estado en nuevos documentos fechados.',
              '- Investigación nueva bajo `research/<pregunta>/`, con subcarpetas de campaña/ejecución y sus contratos; mantener separados fuente, análisis, resultado y evidencia. Los directorios históricos conservan sus rutas y IDs.',
              '- Capturas privadas o nominales en las rutas locales excluidas de Git. Nunca convertir el catálogo en un inventario público de esas capturas.',
              '- Evidencias inmutables conservan bytes, hashes y commit. No moverlas para que el árbol parezca más limpio ni usarlas como código activo.',
              '- Tras añadir, renombrar o retirar archivos versionados: preparar el cambio en Git, regenerar índice y ejecutar `check`. Un índice antiguo debe fallar de forma visible.', '']
    return '\n'.join(lines)


def research_markdown(catalogue):
    groups = {}
    for x in catalogue['files']:
        parts = PurePosixPath(x['path']).parts
        if len(parts) >= 3 and parts[0] == 'research':
            groups.setdefault(parts[1], []).append(x['path'])
    lines = ['# Índice de investigación', '',
             'Generado desde archivos versionados. Un directorio o informe no demuestra una ejecución ni un hallazgo. Consultar [el estado vivo](../PROJECT_STATE.json) para la pregunta activa y [el mapa](../PROJECT_MAP.md) para el producto.', '',
             '| Serie/pregunta histórica | Archivos | Entradas documentales |', '| --- | ---: | --- |']
    for group, paths in sorted(groups.items()):
        entries = [x for x in paths if any(token in PurePosixPath(x).name.upper() for token in ('FINAL_REPORT', 'REPORT.MD', 'CAMPAIGN_STATUS', 'AUTHORIZATION', 'LEDGER.JSON'))][:5]
        links = ', '.join(f'[{PurePosixPath(x).name}]({PurePosixPath(x).relative_to("research").as_posix()})' for x in entries) or f'[Carpeta]({group}/)'
        lines.append(f'| [{group}]({group}/) | {len(paths)} | {links} |')
    lines += ['', 'Los nombres reflejan la organización histórica. No escoger una línea por ser el último directorio: leer el hito de investigación y su criterio de evidencia.', '']
    return '\n'.join(lines)


def render(catalogue):
    return {'PROJECT_INDEX.json': json.dumps(catalogue, ensure_ascii=False, indent=2) + '\n',
            'PROJECT_MAP.md': map_markdown(catalogue), 'research/INDEX.md': research_markdown(catalogue)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('build'); sub.add_parser('check')
    find = sub.add_parser('find'); find.add_argument('query'); find.add_argument('--category', choices=CATEGORIES); find.add_argument('--limit', type=int, default=20)
    args = parser.parse_args()
    catalogue = make_catalogue(tracked_paths())
    if args.command == 'find':
        matches = search(catalogue, args.query, args.category)
        print(json.dumps({'matches': len(matches), 'files': matches[:max(0,args.limit)]}, ensure_ascii=False, indent=2))
        return 0
    stale = []
    for name, content in render(catalogue).items():
        path = PROJECT / name
        if args.command == 'build':
            path.write_text(content, encoding='utf-8', newline='\n')
        elif not path.exists() or path.read_text(encoding='utf-8') != content:
            stale.append(name)
    if stale:
        print('STALE_PROJECT_INDEX: stage intended files, then run build: ' + ', '.join(stale))
        return 1
    print(f'OK {len(catalogue["files"])} tracked files indexed; private/local raw excluded')
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
