"""Compact, derived continuity checks for PFL. Read-only unless `handoff` is requested."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT
sys.path.insert(0, str(ROOT / 'tools' / 'ab_atlas'))
import atlas_delta


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode('utf-8').strip()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def resolve_commit(commit):
    """Resolve a retained original AB SHA through the documented extraction map."""
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit):
        return None
    def exists(value):
        return subprocess.run(['git','cat-file','-e',value+'^{commit}'],cwd=ROOT,
                              stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode == 0
    if exists(commit):
        return commit
    mapping = PROJECT / 'docs/migration/COMMIT_MAP.tsv'
    if mapping.is_file():
        for line in mapping.read_text(encoding='utf-8').splitlines()[1:]:
            old, new = line.split()
            if old == commit and new != '0'*40 and exists(new):
                return new
    return None


def validate_state(state, observed_atlas, observed_budget, project=PROJECT):
    errors = []
    if state.get('schema') != 'pfl.project_state.v1':
        errors.append('Unsupported state schema')
    if state.get('atlas_snapshot') != observed_atlas:
        errors.append('STALE_ATLAS: refresh snapshot only after actual canonical replay')
    if state.get('authorization_snapshot') != observed_budget:
        errors.append('STALE_BUDGET: use the original authorization ledger; do not reset or spend by inference')
    values = [observed_budget.get(k) for k in ('authorized', 'executed', 'remaining', 'historical_separate_stop_r5')]
    if any(type(x) is not int or x < 0 for x in values) or values[0] != values[1] + values[2]:
        errors.append('INCONSISTENT_AUTHORIZATION: granted must equal executed plus remaining; legacy is separate')
    milestones = state.get('milestones', [])
    ids = [m.get('id') for m in milestones]
    if len(ids) != len(set(ids)):
        errors.append('Duplicate milestone IDs')
    dependencies = {m.get('id'): m.get('dependencies', []) for m in milestones}
    if any(d not in dependencies for ds in dependencies.values() for d in ds):
        errors.append('Unknown milestone dependency')
    visiting, visited = set(), set()
    def visit(key):
        if key in visiting:
            return False
        if key in visited:
            return True
        visiting.add(key)
        if any(not visit(d) for d in dependencies.get(key, [])):
            return False
        visiting.remove(key); visited.add(key)
        return True
    if not all(visit(key) for key in dependencies):
        errors.append('Cyclic milestone dependencies')
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
            commit = m.get('verified_commit', '')
            if resolve_commit(commit) is None:
                errors.append(f'Unknown completion commit: {m.get("id")}')
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


def publication_observation(verified_commit):
    """Describe a local Git ref, never pretend that a static briefing queried GitHub."""
    for ref in ('refs/remotes/origin/main', 'refs/heads/main'):
        result = subprocess.run(['git', 'rev-parse', '--verify', ref], cwd=ROOT, capture_output=True)
        if result.returncode == 0:
            resolved = resolve_commit(verified_commit)
            included = bool(resolved) and subprocess.run(['git', 'merge-base', '--is-ancestor', resolved, ref],
                                                         cwd=ROOT, capture_output=True).returncode == 0
            return {'main_ref': ref, 'main_head': result.stdout.decode().strip(),
                    'reviewed_commit_in_main': included, 'scope': 'LOCAL_GIT_REF_FETCH_REQUIRED'}
    return {'main_ref': None, 'main_head': None, 'reviewed_commit_in_main': None,
            'scope': 'NO_LOCAL_MAIN_REF'}


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
    catalogue = subprocess.run([sys.executable, str(PROJECT / 'scripts/project_index.py'), 'check'],
                               cwd=ROOT, capture_output=True)
    if catalogue.returncode:
        errors.append('STALE_PROJECT_INDEX: stage intended files and rebuild the project catalogue')
    code_paths = ['tools/ab_atlas', 'src', 'tests', 'scripts', 'pyproject.toml']
    names = subprocess.check_output(['git', 'ls-files', '-z', '--', *code_paths], cwd=ROOT).decode().split('\0')
    digest = hashlib.sha256()
    for name in sorted(n for n in names if n and (ROOT / n).is_file()):
        digest.update(name.encode()); digest.update(b'\0'); digest.update((ROOT / name).read_bytes())
    return state, {'branch': git('branch', '--show-current'), 'head': git('rev-parse', 'HEAD'),
                   'atlas': atlas, 'authorization': budget, 'code_fingerprint': digest.hexdigest(),
                   'publication': publication_observation(state['latest_validation'].get('verified_commit', 'HEAD')),
                   'errors': errors, 'note': 'Metadata consistency only; does not execute product tests, validate rights, or authorize release.'}


def brief(state, observed):
    lines = ['# PFL · briefing derivado', '', f"Rama: `{observed['branch']}`; HEAD: `{observed['head']}`.",
             f"Estado rev. {state['revision']}; publicación declarada: {state['publication_status']}.",
             f"Código revisado incluido en {observed['publication']['main_ref']}: {observed['publication']['reviewed_commit_in_main']} (referencia local; hacer fetch).", '',
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
