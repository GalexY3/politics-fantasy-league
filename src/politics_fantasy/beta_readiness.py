"""Read-only startup preflight for the local, synthetic PFL beta.

The contract deliberately separates observed local runtime checks from the
versioned scientific and public-release gates. A passing local preflight never
grants rights to original data, empirical AB cycles or public deployment.
"""
from __future__ import annotations

from contextlib import closing
import json
from pathlib import Path
import sqlite3

from .progress_api import progress_status

PROJECT = Path(__file__).resolve().parents[2]
RELEASE_GATES = PROJECT / 'product/release_gates_v1_20261028.json'
SYSTEM20_LEDGER = PROJECT / 'research/PFL_SYSTEM20_20261031/AUTHORIZATION.json'
PROJECT_STATE = PROJECT / 'PROJECT_STATE.json'
EXPECTED_GATES = frozenset({
    'G01_REGISTRY_RIGHTS', 'G02_REAL_IDENTITY', 'G03_REAL_EVENTS',
    'G04_MULTIUSER_AUTH', 'G05_E2E_ACTUAL', 'G06_HOSTING_PILOT',
})
WEB_ASSETS = ('index.html', 'app.js', 'style.css')


class BetaReadinessUnavailable(RuntimeError):
    """One of the bounded public readiness authorities cannot be verified."""


def _authority(path: Path, schema: str) -> dict:
    try:
        if not path.is_file() or not 0 < path.stat().st_size <= 200_000:
            raise BetaReadinessUnavailable('AUTHORITY_UNAVAILABLE')
        payload = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(payload, dict) or payload.get('schema') != schema:
            raise BetaReadinessUnavailable('AUTHORITY_INVALID')
        return payload
    except (OSError, ValueError, UnicodeError, TypeError) as exc:
        raise BetaReadinessUnavailable('AUTHORITY_UNAVAILABLE') from exc


def _accounts_schema_ready(path: Path | None) -> bool:
    if path is None:
        return False
    try:
        path = Path(path)
        if not path.is_file():
            return False
        # Read-only SQLite URI: never create, migrate or query account rows.
        with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro',
                                     uri=True, timeout=0.25)) as db:
            tables = {row[0] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name IN ('account','account_session')")}
            if tables != {'account', 'account_session'}:
                return False
            account_columns = {row[1] for row in db.execute('PRAGMA table_info(account)')}
            session_columns = {row[1] for row in db.execute('PRAGMA table_info(account_session)')}
        return ({'user_id', 'handle', 'password_salt', 'password_hash', 'created_at'}
                <= account_columns and
                {'session_hash', 'user_id', 'csrf_secret', 'expires_at'}
                <= session_columns)
    except (OSError, ValueError, sqlite3.Error):
        return False


def beta_readiness(*, bind_host: str, accounts_path: Path | None,
                   web_root: Path, release_path: Path = RELEASE_GATES,
                   ledger_path: Path = SYSTEM20_LEDGER,
                   state_path: Path = PROJECT_STATE,
                   progress_path: Path | None = None) -> dict:
    """Return a bounded anonymous status; never expose paths or account data."""
    gates_doc = _authority(Path(release_path), 'pfl.release_gates.v1')
    gates = gates_doc.get('gates')
    if (not isinstance(gates, list) or len(gates) != 6 or
            any(not isinstance(gate, dict) or
                not isinstance(gate.get('id'), str) or
                gate.get('status') not in ('BLOCKED', 'PASSED', 'READY_REVIEW')
                for gate in gates) or
            {gate.get('id') for gate in gates} != EXPECTED_GATES):
        raise BetaReadinessUnavailable('GATES_INVALID')

    ledger = _authority(Path(ledger_path), 'pfl.authorization.v1')
    if ledger.get('id') != 'PFL-SYSTEM20-20261031':
        raise BetaReadinessUnavailable('LEDGER_INVALID')
    counts = ('authorized', 'executed_valid', 'invalid', 'planning_only', 'remaining')
    if (any(type(ledger.get(k)) is not int or ledger[k] < 0 for k in counts)
            or sum(ledger[k] for k in counts[1:]) != ledger['authorized']):
        raise BetaReadinessUnavailable('LEDGER_INVALID')

    state = _authority(Path(state_path), 'pfl.project_state.v1')
    checkpoint = state.get('scientific_infrastructure_checkpoint')
    if (not isinstance(checkpoint, dict) or
            type(checkpoint.get('round22_R5_stop')) is not bool):
        raise BetaReadinessUnavailable('R5_STATUS_UNVERIFIED')

    progress = progress_status(progress_path)
    if (progress.get('ok') is not True or
            progress.get('real_people_scoring_ready') is not False or
            not isinstance(progress.get('release_blockers'), list)):
        raise BetaReadinessUnavailable('PROGRESS_UNVERIFIED')

    runtime_checks = {
        'loopback_binding': bind_host == '127.0.0.1',
        'accounts_schema_readable': _accounts_schema_ready(accounts_path),
        'web_assets_present': all(
            (Path(web_root) / name).is_file() and
            (Path(web_root) / name).stat().st_size > 0
            for name in WEB_ASSETS),
    }
    runtime_ready = all(runtime_checks.values())
    # These are solely manifest claims. The GET handler cannot independently
    # corroborate their issuer, rights or suitability for deployment.
    recorded_attestations = sum(bool(gate.get('attestation') and gate.get('reviewed_by'))
                                and gate['status'] == 'PASSED' for gate in gates)
    return {
        'schema': 'pfl.beta_readiness.v1',
        'ok': runtime_ready,
        'local_runtime': {
            'status': 'READY_FOR_LOCAL_PREFLIGHT' if runtime_ready else 'UNAVAILABLE',
            'scope': 'LOOPBACK_SYNTHETIC_DEMO',
            'checks': runtime_checks,
            'anonymous_readiness_get': True,
            'full_user_journey_attested': False,
        },
        'scientific_admission': {
            'r5_status': ('STOP_R5' if checkpoint['round22_R5_stop']
                          else 'NO_CURRENT_R5_ATTESTATION'),
            'r5_record': 'R22',
            'system20_valid_ab_cycles': ledger['executed_valid'],
            'system20_remaining_ab_cycles': ledger['remaining'],
            'empirical_study_eligible': False,
        },
        'public_release': {
            'status': 'BLOCKED_PENDING_INDEPENDENT_ATTESTATION',
            'eligible': False,
            'gates_with_attestation_records': recorded_attestations,
            'gates_total': len(gates),
            'progress_release_blockers': len(progress['release_blockers']),
            'real_person_scoring': False,
            'public_hosting_authorized': False,
        },
    }
