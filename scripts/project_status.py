"""Compact, derived continuity checks for PFL. Read-only unless `handoff` is requested."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
sys.path.insert(0, str(ROOT / 'ab_atlas'))
import atlas_delta


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode('utf-8').strip()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def validate_state(state, observed_atlas, observed_budget, project=PROJECT):
    errors = []
    if state.get('schema') != 'pfl.project_state.v1':
        errors.append('Unsupported state schema')
    if state.get('atlas_snapshot') != observed_atlas:
        errors.append('STALE_ATLAS: refresh snapshot only after actual canonical replay')
    if state.get('authorization_snapshot') != observed_budget:
        errors.append('STALE_BUDGET: use the original authorization ledger; do not reset or spend by inference')
    milestones = state.get('milestones', [])
    ids = [m.get('id') for m in milestones]
    if len(ids) != len(set(ids)):
        errors.append('Duplicate milestone IDs')
    for lane in ('product', 'research'):
        active = [m for m in milestones if m.get('lane') == lane and m.get('status') == 'IN_PROGRESS']
        if len(active) > 1:
            errors.append(f'Too much active work in {lane}')
    for m in milestones:
        if m.get('status') not in {'QUEUED', 'IN_PROGRESS', 'READY_REVIEW', 'DONE', 'BLOCKED', 'PARKED'}:
            errors.append(f'Unknown status: {m.get("id")}')
        if m.get('status') in {'BLOCKED', 'PARKED'} and not m.get('reopen_when'):
            errors.append(f'Blocked milestone without reopening condition: {m.get("id")}')
        if m.get('status') == 'DONE':
            evidence = m.get('evidence', [])
            if not evidence or not m.get('verified_commit'):
                errors.append(f'Unsubstantiated completion: {m.get("id")}')
            for ref in evidence:
                if ref.startswith('https://'):
                    continue  # URL existence is not attested by this offline check.
                target = (project / ref).resolve()
                if not target.is_relative_to(project.resolve()) or not target.is_file():
                    errors.append(f'Missing local completion evidence: {m.get("id")} / {ref}')
    graph = load(project / state['o7_graph'])
    graph_ids = [n['id'] for n in graph['nodes']]
    edge_keys = [(e['from'], e['to'], e['relation']) for e in graph['edges']]
    if len(graph_ids) != len(set(graph_ids)) or len(edge_keys) != len(set(edge_keys)):
        errors.append('O7 duplicate IDs/edges')
    if any(a not in graph_ids or b not in graph_ids for a, b, _ in edge_keys):
        errors.append('O7 dangling reference')
    for ref in state['required_entry_files']:
        if not (project / ref).is_file():
            errors.append(f'Missing continuity entry: {ref}')
    return errors


def derive():
    state = load(PROJECT / 'PROJECT_STATE.json')
    doc, batches = atlas_delta.replay(PROJECT / 'ab_atlas/seed.json', PROJECT / 'ab_atlas/updates')
    atlas = {'batches': len(batches), 'nodes': len(doc['nodes']), 'edges': len(doc['edges']),
             'runs': len(doc['runs']), 'complaints': len(doc['complaints']),
             'state_sha256': atlas_delta.digest(doc),
             'passed_gates': sum(g['status'] == 'passed' for g in doc['project_contract']['release_gates'])}
    ledger = load(PROJECT / state['authorization_ledger'])
    budget = {'campaign': 'ABH10', 'authorized': ledger['user_authorized_new'],
              'executed': ledger['executed_new'], 'remaining': ledger['new_remaining'],
              'historical_separate_stop_r5': ledger['historical_legacy_separate_STOP_R5']}
    errors = validate_state(state, atlas, budget)
    code_paths = ['ab_atlas', 'proyectos/politics-fantasy-league/src',
                  'proyectos/politics-fantasy-league/tests', 'proyectos/politics-fantasy-league/scripts',
                  'proyectos/politics-fantasy-league/pyproject.toml']
    names = subprocess.check_output(['git', 'ls-files', '-z', '--', *code_paths], cwd=ROOT).decode().split('\0')
    digest = hashlib.sha256()
    for name in sorted(n for n in names if n and (ROOT / n).is_file()):
        digest.update(name.encode()); digest.update(b'\0'); digest.update((ROOT / name).read_bytes())
    return state, {'branch': git('branch', '--show-current'), 'head': git('rev-parse', 'HEAD'),
                   'atlas': atlas, 'authorization': budget, 'code_fingerprint': digest.hexdigest(),
                   'errors': errors, 'note': 'Metadata consistency only; does not execute product tests, validate rights, or authorize release.'}


def brief(state, observed):
    lines = ['# PFL · briefing derivado', '', f"Rama: `{observed['branch']}`; HEAD: `{observed['head']}`.",
             f"Estado rev. {state['revision']}; integración pendiente de revisión según GitHub.", '',
             f"Atlas: {observed['atlas']['batches']} lotes; SHA `{observed['atlas']['state_sha256']}`; gates {observed['atlas']['passed_gates']}/6.",
             f"Autorización ABH10: {observed['authorization']['executed']}/{observed['authorization']['authorized']} ejecutados; {observed['authorization']['remaining']} disponibles, preservados bajo R5. Históricos separados: {observed['authorization']['historical_separate_stop_r5']}.", '']
    for lane in ('product', 'research'):
        lines.append(f'## {lane}')
        for m in state['milestones']:
            if m['lane'] == lane:
                lines.append(f"- {m['id']} [{m['status']}]: {m['outcome']}. Siguiente: {m['next_action']}")
        lines.append('')
    lines += ['## Última validación declarada', state['latest_validation']['summary'], '',
              'Este briefing consulta el árbol local y el ledger; hacer fetch/resolver HEAD remoto antes de usarlo para continuar. Un resultado histórico no verifica otro commit.', '',
              'Consistencia: ' + ('PASS' if not observed['errors'] else '; '.join(observed['errors'])),
              'Huella código/tests: `' + observed['code_fingerprint'] + '`.',
              'No pedir ciclos por fórmula. Aparcar bloqueos sin observación nueva. Actualizar PROJECT_STATE y este handoff al cerrar.']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'brief', 'json', 'handoff'])
    args = parser.parse_args()
    state, observed = derive()
    if args.command == 'handoff':
        if observed['errors']:
            raise SystemExit('Refusing stale handoff: ' + '; '.join(observed['errors']))
        (PROJECT / 'HANDOFF.md').write_text(brief(state, observed), encoding='utf-8', newline='\n')
        print('HANDOFF.md written; commit it with PROJECT_STATE.json')
    elif args.command == 'brief':
        print(brief(state, observed))
    else:
        print(json.dumps(observed, ensure_ascii=False, indent=2))
    return int(bool(observed['errors']))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
