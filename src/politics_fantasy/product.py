"""Single-machine, synthetic-demo fantasy engine with transactional SQLite state.

NO authentication, internet deployment, validated official parsers, nor real-politician scores.
All demo entities and events are explicitly fictional. Launch on loopback only.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass

from .events import PoliticalEvent, as_utc
from .scoring import DEMO_RULE, person_week_points

UTC = timezone.utc
MAX_OWNED = 5
LINEUP_SIZE = 3
STARTING_CREDITS = 100
DATA_PROVENANCE = "SYNTHETIC_FICTIONAL_DEMO_ONLY"
NAMES = [
    ("F01", "Figura Demo 01", "Portavocía", "Grupo Índigo", 23),
    ("F02", "Figura Demo 02", "Diputación", "Grupo Ocre", 17),
    ("F03", "Figura Demo 03", "Comisión", "Grupo Índigo", 28),
    ("F04", "Figura Demo 04", "Diputación", "Grupo Verde", 12),
    ("F05", "Figura Demo 05", "Portavocía", "Grupo Ocre", 22),
    ("F06", "Figura Demo 06", "Comisión", "Grupo Verde", 19),
    ("F07", "Figura Demo 07", "Diputación", "Grupo Índigo", 15),
    ("F08", "Figura Demo 08", "Portavocía", "Grupo Verde", 25),
    ("F09", "Figura Demo 09", "Comisión", "Grupo Ocre", 14),
    ("F10", "Figura Demo 10", "Diputación", "Grupo Verde", 16),
]
SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS figure(
  id TEXT PRIMARY KEY, display_name TEXT NOT NULL, role TEXT NOT NULL,
  group_name TEXT NOT NULL, price INTEGER NOT NULL CHECK(price>0),
  evidence_state TEXT NOT NULL CHECK(evidence_state='SYNTHETIC'));
CREATE TABLE IF NOT EXISTS club(
  id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE,
  credits INTEGER NOT NULL CHECK(credits>=0));
CREATE TABLE IF NOT EXISTS ownership(
  figure_id TEXT PRIMARY KEY REFERENCES figure(id),
  club_id TEXT NOT NULL REFERENCES club(id), bought_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS fantasy_round(
  id TEXT PRIMARY KEY, name TEXT NOT NULL, starts_at TEXT NOT NULL,
  ends_at TEXT NOT NULL, lock_at TEXT NOT NULL,
  coverage_state TEXT NOT NULL CHECK(coverage_state IN('SYNTHETIC_COMPLETE','NOT_AVAILABLE')));
CREATE TABLE IF NOT EXISTS lineup(
  club_id TEXT NOT NULL REFERENCES club(id),
  round_id TEXT NOT NULL REFERENCES fantasy_round(id),
  figure_id TEXT NOT NULL REFERENCES figure(id),
  PRIMARY KEY(club_id,round_id,figure_id));
CREATE TABLE IF NOT EXISTS demo_event(
  event_id TEXT PRIMARY KEY, figure_id TEXT NOT NULL REFERENCES figure(id),
  kind TEXT NOT NULL, occurred_at TEXT NOT NULL,
  first_public_at TEXT NOT NULL, raw_sha256 TEXT NOT NULL,
  source_url TEXT NOT NULL, source_version TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS trade(
  id INTEGER PRIMARY KEY AUTOINCREMENT, club_id TEXT NOT NULL REFERENCES club(id),
  figure_id TEXT NOT NULL REFERENCES figure(id), action TEXT NOT NULL,
  credits_delta INTEGER NOT NULL, occurred_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_demo_event_time ON demo_event(occurred_at, first_public_at);
CREATE INDEX IF NOT EXISTS idx_lineup_round ON lineup(round_id,club_id);
CREATE TABLE IF NOT EXISTS demo_clock(
  id INTEGER PRIMARY KEY CHECK(id=1), offset_seconds INTEGER NOT NULL CHECK(offset_seconds>=0));
INSERT OR IGNORE INTO demo_clock VALUES(1,0);
CREATE TABLE IF NOT EXISTS round_settlement(
  round_id TEXT PRIMARY KEY REFERENCES fantasy_round(id),
  next_round_id TEXT NOT NULL UNIQUE REFERENCES fantasy_round(id),
  settled_at TEXT NOT NULL, rule_version TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS round_settlement_score(
  round_id TEXT NOT NULL REFERENCES round_settlement(round_id),
  club_id TEXT NOT NULL REFERENCES club(id), score REAL,
  PRIMARY KEY(round_id,club_id));
CREATE TABLE IF NOT EXISTS round_settlement_component(
  round_id TEXT NOT NULL REFERENCES round_settlement(round_id),
  club_id TEXT NOT NULL REFERENCES club(id),
  figure_id TEXT NOT NULL REFERENCES figure(id),
  points REAL NOT NULL CHECK(points>=0),
  PRIMARY KEY(round_id,club_id,figure_id));
"""


class GameError(ValueError):
    def __init__(self, code: str, message: str, status: int = 400):
        super().__init__(message)
        self.code, self.status = code, status


@contextmanager
def connect(path: Path):
    con = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA busy_timeout=5000")
    try:
        yield con
    finally:
        con.close()


def utc_now() -> datetime:
    return datetime.now(UTC)


def stamp(dt: datetime) -> str:
    return as_utc(dt).isoformat(timespec='seconds')


def _game_now(db: sqlite3.Connection, when: datetime | None = None) -> datetime:
    """Simulation time is explicit and persisted; tests may supply wall time."""
    offset = db.execute('SELECT offset_seconds FROM demo_clock WHERE id=1').fetchone()
    return as_utc(when or utc_now()) + timedelta(seconds=offset[0] if offset else 0)


def seed_demo(path: Path, *, now: datetime | None = None) -> None:
    """Idempotent fixture; DO NOT use as validated political observations."""
    now = as_utc(now or utc_now())
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.executescript(SCHEMA)
        # A nonempty figure table alone does not prove the demo seeded fully.
        # Fail closed on partial/corrupted fixtures; never silently reset user state.
        counts = {table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                  for table in ("figure", "club", "fantasy_round", "demo_event")}
        if counts["figure"]:
            if (counts["figure"] != len(NAMES) or counts["club"] < 1
                    or counts["fantasy_round"] < 2 or counts["demo_event"] < 8):
                raise GameError("PARTIAL_SEED", "Demo local incompleta; revisar antes de iniciar.", 409)
            return
        if any(counts.values()):
            raise GameError("PARTIAL_SEED", "Demo local incompleta; revisar antes de iniciar.", 409)
        db.execute("BEGIN IMMEDIATE")
        try:
            db.executemany("INSERT INTO figure VALUES(?,?,?,?,?,'SYNTHETIC')", NAMES)
            db.execute("INSERT INTO club VALUES('demo','Club Demostración',?)", (STARTING_CREDITS - 23 - 17 - 28,))
            for fig in ['F01', 'F02', 'F03']:
                db.execute("INSERT INTO ownership VALUES(?,'demo',?)", (fig, stamp(now)))
            prior_start = now - timedelta(days=14)
            prior_end = now - timedelta(days=7)
            next_start = now + timedelta(days=2)
            next_end = now + timedelta(days=9)
            db.executemany("INSERT INTO fantasy_round VALUES(?,?,?,?,?,?)", [
                ('past','Jornada de demostración cerrada',stamp(prior_start),stamp(prior_end),stamp(prior_start-timedelta(hours=1)),'SYNTHETIC_COMPLETE'),
                ('next','Próxima jornada de demostración',stamp(next_start),stamp(next_end),stamp(next_start-timedelta(hours=1)),'NOT_AVAILABLE')
            ])
            for fig in ['F01','F02','F03']:
                db.execute("INSERT INTO lineup VALUES('demo','past',?)", (fig,))
            # Synthetic events intentionally have synthetically fabricated timestamps + hashes.
            # This fixture must NEVER be passed to research labels as institutional evidence.
            for idx, (fig, kind, offset) in enumerate([
                ('F01','speech_recorded',1),('F01','speech_recorded',2),
                ('F02','question_registered',2),('F02','initiative_registered',4),
                ('F03','speech_recorded',1),('F03','initiative_registered',3),
                ('F03','question_registered',5),('F04','speech_recorded',2),
            ]):
                when = prior_start + timedelta(days=offset)
                db.execute("INSERT INTO demo_event VALUES(?,?,?,?,?,?,?,?)",
                           (f'SYN-{idx+1:03}',fig,kind,stamp(when),stamp(when+timedelta(hours=2)),
                            f'{idx+1:064x}','synthetic://fixture','synthetic-demo-1'))
            db.execute('COMMIT')
        except Exception:
            db.execute('ROLLBACK')
            raise


def _get(db: sqlite3.Connection, table: str, key: str):
    if table not in {'club','figure','fantasy_round'}:
        raise ValueError('Invalid table')
    if not isinstance(key, str) or not key:
        raise GameError('INVALID_ID','El identificador debe ser una cadena no vacía.')
    return db.execute(f'SELECT * FROM {table} WHERE id=?', (key,)).fetchone()


def add_club(path: Path, name: str) -> dict:
    original = name if isinstance(name, str) else ''
    name = original.strip()
    if (any(ord(x) < 32 or ord(x) == 127 for x in original) or not (3 <= len(name) <= 36)
            or any(ch in '<>' for ch in name)):
        raise GameError('INVALID_CLUB_NAME','Nombre de club: 3–36 caracteres, sin HTML ni controles.')
    cid = str(uuid.uuid4())
    with connect(path) as db:
        try:
            db.execute("INSERT INTO club VALUES(?,?,?)", (cid,name,STARTING_CREDITS))
        except sqlite3.IntegrityError:
            raise GameError('DUPLICATE_NAME','Ya existe un club con ese nombre.',409) from None
    return {'id':cid,'name':name,'credits':STARTING_CREDITS}


def transfer(path: Path, *, club_id: str, figure_id: str, action: str, when: datetime | None = None) -> dict:
    if action not in ('buy','sell'):
        raise GameError('INVALID_ACTION','Acción no reconocida')
    with connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        try:
            now = _game_now(db, when)
            club = _get(db,'club',club_id)
            figure = _get(db,'figure',figure_id)
            if club is None or figure is None:
                raise GameError('UNKNOWN_ENTITY','Club o figura inexistente.',404)
            owner = db.execute('SELECT club_id FROM ownership WHERE figure_id=?',(figure_id,)).fetchone()
            if action == 'buy':
                if owner:
                    raise GameError('OWNED','La figura ya pertenece a un club.',409)
                count = db.execute('SELECT COUNT(*) FROM ownership WHERE club_id=?',(club_id,)).fetchone()[0]
                if count >= MAX_OWNED:
                    raise GameError('ROSTER_FULL','Plantilla completa.',409)
                if club['credits'] < figure['price']:
                    raise GameError('LOW_CREDITS','Créditos insuficientes.',409)
                delta = -figure['price']
                db.execute('INSERT INTO ownership VALUES(?,?,?)',(figure_id,club_id,stamp(now)))
            else:
                if not owner or owner['club_id'] != club_id:
                    raise GameError('NOT_OWNED','Esa figura no pertenece al club.',409)
                # Preserve an invariant across the future lock: a player cannot be
                # sold while included in a still-editable lineup. Historical,
                # already-locked lineups remain frozen and may be sold afterwards.
                future = db.execute('''SELECT 1 FROM lineup l JOIN fantasy_round r
                            ON r.id=l.round_id WHERE l.club_id=? AND l.figure_id=?
                            AND r.lock_at>? LIMIT 1''',(club_id,figure_id,stamp(now))).fetchone()
                if future:
                    raise GameError('ACTIVE_LINEUP','Modifica primero la alineación futura antes de vender.',409)
                delta = figure['price']
                db.execute('DELETE FROM ownership WHERE figure_id=?',(figure_id,))
            db.execute('UPDATE club SET credits=credits+? WHERE id=?',(delta,club_id))
            db.execute('INSERT INTO trade(club_id,figure_id,action,credits_delta,occurred_at) VALUES(?,?,?,?,?)',
                       (club_id,figure_id,action,delta,stamp(now)))
            credits = db.execute('SELECT credits FROM club WHERE id=?',(club_id,)).fetchone()[0]
            db.execute('COMMIT')
            return {'club_id':club_id,'figure_id':figure_id,'action':action,'credits_delta':delta,'credits':credits}
        except Exception:
            db.execute('ROLLBACK')
            raise


def set_lineup(path: Path, *, club_id: str, round_id: str, figures: list[str],
               when: datetime | None = None) -> dict:
    if (not isinstance(figures, list) or len(figures) != LINEUP_SIZE
            or not all(isinstance(f,str) for f in figures) or len(set(figures)) != LINEUP_SIZE):
        raise GameError('BAD_LINEUP',f'El once reducido exige {LINEUP_SIZE} figuras distintas.')
    with connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        try:
            now = _game_now(db, when)
            if not _get(db,'club',club_id):
                raise GameError('UNKNOWN_CLUB','Club inexistente.',404)
            rnd = _get(db,'fantasy_round',round_id)
            if rnd is None:
                raise GameError('UNKNOWN_ROUND','Jornada inexistente.',404)
            if now >= as_utc(rnd['lock_at']):
                raise GameError('LINEUP_LOCKED','La jornada ya ha bloqueado sus alineaciones.',409)
            owned = {x[0] for x in db.execute('SELECT figure_id FROM ownership WHERE club_id=?',(club_id,))}
            if not set(figures) <= owned:
                raise GameError('NOT_OWNED','Solo puedes alinear figuras que posees.',409)
            db.execute('DELETE FROM lineup WHERE club_id=? AND round_id=?',(club_id,round_id))
            db.executemany('INSERT INTO lineup VALUES(?,?,?)',[(club_id,round_id,f) for f in figures])
            db.execute('COMMIT')
            return {'club_id':club_id,'round_id':round_id,'figures':sorted(figures),'locked':False}
        except Exception:
            db.execute('ROLLBACK')
            raise


def _round_score(db: sqlite3.Connection, rnd: sqlite3.Row, figures: list[str], *, now: datetime) -> float | None:
    if rnd['coverage_state'] != 'SYNTHETIC_COMPLETE' or now < as_utc(rnd['ends_at']):
        return None
    events=[]
    start=as_utc(rnd['starts_at'])
    end=as_utc(rnd['ends_at'])
    for e in db.execute('SELECT * FROM demo_event'):
        occurred=as_utc(e['occurred_at'])
        # Reject relevant non-fictional records, but never parse an unrelated
        # future/past event into this round's score or let it block settlement.
        if not start <= occurred < end:
            continue
        if not e['source_url'].startswith('synthetic://'):
            return None
        events.append(PoliticalEvent(e['event_id'],e['kind'],as_utc(e['occurred_at']),as_utc(e['first_public_at']),
                                     (e['figure_id'],),e['source_url'],e['raw_sha256'],e['source_version'],
                                     {'evidence':'SYNTHETIC_ONLY'}))
    end=as_utc(rnd['ends_at'])
    cutoff = min(now, end + timedelta(days=1))
    return sum(person_week_points(events, person_id=f, start=as_utc(rnd['starts_at']),end=end,
                                  knowledge_cutoff=cutoff, rule=DEMO_RULE) for f in figures)


def simulate_round(path: Path, *, round_id: str, when: datetime | None = None) -> dict:
    """Explicitly simulate one fictional round; atomically freeze and open the next.

    `when` is an optional wall clock for tests. The stored offset advances only
    the demo clock, never the system clock or any real-world political source.
    """
    with connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        try:
            rnd = _get(db, 'fantasy_round', round_id)
            if rnd is None:
                raise GameError('UNKNOWN_ROUND', 'Jornada inexistente.', 404)
            previous = db.execute('SELECT * FROM round_settlement WHERE round_id=?', (round_id,)).fetchone()
            if previous:
                db.execute('COMMIT')
                return {'round_id': round_id, 'next_round_id': previous['next_round_id'],
                        'settled_at': previous['settled_at'], 'already_settled': True}
            latest = db.execute('SELECT id FROM fantasy_round ORDER BY starts_at DESC, id DESC LIMIT 1').fetchone()
            if latest is None or latest['id'] != round_id or rnd['coverage_state'] != 'NOT_AVAILABLE':
                raise GameError('ROUND_NOT_SIMULATABLE', 'Solo se puede simular la jornada pendiente actual.', 409)
            start, end, lock = map(as_utc, (rnd['starts_at'], rnd['ends_at'], rnd['lock_at']))
            if end - start < timedelta(hours=1) or lock > start:
                raise GameError('INVALID_ROUND_DATES', 'Fechas de jornada inválidas.', 409)
            for event in db.execute('SELECT occurred_at,source_url FROM demo_event'):
                if start <= as_utc(event['occurred_at']) < end and not event['source_url'].startswith('synthetic://'):
                    raise GameError('NON_SYNTHETIC_EVENT', 'La jornada contiene una fuente no ficticia.', 409)
            wall = as_utc(when or utc_now())
            current = _game_now(db, wall)
            cutoff = max(current, end + timedelta(seconds=1))
            offset = max(0, math.ceil((cutoff - wall).total_seconds()))
            cutoff = wall + timedelta(seconds=offset)
            db.execute('UPDATE demo_clock SET offset_seconds=? WHERE id=1', (offset,))
            for index, figure in enumerate(db.execute('SELECT id FROM figure ORDER BY id').fetchall()):
                identifier = f'SIM:{round_id}:{figure["id"]}'
                kind = ('speech_recorded', 'question_registered', 'initiative_registered')[index % 3]
                occurred = end - timedelta(minutes=30)
                digest = hashlib.sha256(identifier.encode('utf-8')).hexdigest()
                db.execute('INSERT INTO demo_event VALUES(?,?,?,?,?,?,?,?)',
                           (identifier, figure['id'], kind, stamp(occurred), stamp(occurred), digest,
                            'synthetic://simulated-round', 'synthetic-round-1'))
            db.execute("UPDATE fantasy_round SET coverage_state='SYNTHETIC_COMPLETE' WHERE id=?", (round_id,))
            next_id = 'round-' + uuid.uuid4().hex
            next_start = cutoff + timedelta(days=2)
            db.execute('INSERT INTO fantasy_round VALUES(?,?,?,?,?,?)',
                       (next_id, 'Jornada de demostración siguiente', stamp(next_start),
                        stamp(next_start + timedelta(days=7)), stamp(next_start - timedelta(hours=1)), 'NOT_AVAILABLE'))
            db.execute('INSERT INTO round_settlement VALUES(?,?,?,?)',
                       (round_id, next_id, stamp(cutoff), DEMO_RULE.version))
            updated = _get(db, 'fantasy_round', round_id)
            # Existing account stores lack this table; create it only during
            # explicit settlement, never during GET/state reads.
            db.execute("""CREATE TABLE IF NOT EXISTS round_settlement_component(
                round_id TEXT NOT NULL REFERENCES round_settlement(round_id),
                club_id TEXT NOT NULL REFERENCES club(id),
                figure_id TEXT NOT NULL REFERENCES figure(id),
                points REAL NOT NULL CHECK(points>=0),
                PRIMARY KEY(round_id,club_id,figure_id))""")
            for club in db.execute('SELECT id FROM club').fetchall():
                figures = [row[0] for row in db.execute(
                    'SELECT figure_id FROM lineup WHERE round_id=? AND club_id=? ORDER BY figure_id',
                    (round_id, club['id']))]
                score = _round_score(db, updated, figures, now=cutoff) if len(figures) == LINEUP_SIZE else None
                db.execute('INSERT INTO round_settlement_score VALUES(?,?,?)', (round_id, club['id'], score))
                if score is not None:
                    components = [(fig, _round_score(db, updated, [fig], now=cutoff)) for fig in figures]
                    if (any(points is None for _, points in components)
                            or not math.isclose(sum(points for _, points in components),
                                                score, abs_tol=1e-9)):
                        raise GameError('SCORE_COMPONENT_MISMATCH',
                                        'Desglose ficticio inconsistente; no cerrar.', 409)
                    db.executemany(
                        'INSERT INTO round_settlement_component VALUES(?,?,?,?)',
                        [(round_id, club['id'], fig, points) for fig, points in components])
            db.execute('COMMIT')
            return {'round_id': round_id, 'next_round_id': next_id, 'settled_at': stamp(cutoff),
                    'already_settled': False}
        except Exception:
            db.execute('ROLLBACK')
            raise


def state(path: Path, *, pilot_csv: Path | None = None, when: datetime | None = None) -> dict:
    with connect(path) as db:
        now = _game_now(db, when)
        clock_offset = db.execute('SELECT offset_seconds FROM demo_clock WHERE id=1').fetchone()
        figures=[dict(x) for x in db.execute('SELECT f.*,o.club_id AS owner_id FROM figure f LEFT JOIN ownership o ON o.figure_id=f.id ORDER BY f.id')]
        clubs=[dict(c) for c in db.execute('SELECT * FROM club ORDER BY name')]
        rounds=[]
        has_components = bool(db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='round_settlement_component'"
        ).fetchone())
        for r in db.execute('SELECT * FROM fantasy_round ORDER BY starts_at'):
            rr=dict(r)
            rr['lineups']={}
            rr['scores']={}
            rr['score_details']={}
            rr['is_settled'] = bool(db.execute(
                'SELECT 1 FROM round_settlement WHERE round_id=?', (r['id'],)).fetchone())
            for club in clubs:
                selection=[x[0] for x in db.execute('SELECT figure_id FROM lineup WHERE club_id=? AND round_id=? ORDER BY figure_id',(club['id'],r['id']))]
                rr['lineups'][club['id']]=selection
                frozen = db.execute('SELECT score FROM round_settlement_score WHERE round_id=? AND club_id=?',
                                    (r['id'], club['id'])).fetchone()
                settled = db.execute('SELECT 1 FROM round_settlement WHERE round_id=?', (r['id'],)).fetchone()
                rr['scores'][club['id']] = (frozen['score'] if frozen else None) if settled else (
                    _round_score(db,r,selection,now=now) if len(selection)==LINEUP_SIZE else None)
                detail = {'status':'NOT_SETTLED', 'components':[]}
                if settled:
                    if frozen is None or frozen['score'] is None:
                        detail['status'] = 'NO_VALID_LINEUP'
                    elif not has_components:
                        detail['status'] = 'LEGACY_UNAVAILABLE'
                    else:
                        parts = [dict(x) for x in db.execute(
                            'SELECT figure_id,points FROM round_settlement_component '
                            'WHERE round_id=? AND club_id=? ORDER BY figure_id',
                            (r['id'], club['id']))]
                        if not parts:
                            detail['status'] = 'LEGACY_UNAVAILABLE'
                        elif (len(parts) != LINEUP_SIZE or
                              not math.isclose(sum(p['points'] for p in parts),
                                               frozen['score'], abs_tol=1e-9)):
                            raise GameError('SCORE_COMPONENT_INTEGRITY',
                                            'Desglose ficticio almacenado inconsistente.', 500)
                        else:
                            detail = {'status':'FROZEN_COMPONENTS', 'components':parts,
                                      'rule_version': db.execute(
                                          'SELECT rule_version FROM round_settlement WHERE round_id=?',
                                          (r['id'],)).fetchone()[0]}
                rr['score_details'][club['id']] = detail
            rr['is_locked']=now >= as_utc(r['lock_at'])
            rounds.append(rr)
        # Season classifications use only frozen, settled scores. Historical
        # fixtures and missing lineups never become implicit zeros.
        settled_rounds = [round_info for round_info in rounds if round_info['is_settled']]
        season_standings = []
        for club in clubs:
            observations = [round_info['scores'][club['id']] for round_info in settled_rounds]
            valid = [points for points in observations if points is not None]
            missing = len(observations) - len(valid)
            status = ('NO_SETTLED_ROUNDS' if not observations else
                      'INCOMPLETE_COVERAGE' if missing else 'RANKED')
            season_standings.append({
                'club_id':club['id'], 'club_name':club['name'],
                'total_points':sum(valid) if status=='RANKED' else None,
                'observed_points_lower_bound':sum(valid),
                'rounds_scored':len(valid),'rounds_unknown':missing,
                'rounds_settled':len(observations),
                'status':status,'rank':None})
        season_standings.sort(key=lambda row:(
            row['status']!='RANKED',
            -(row['total_points'] if row['total_points'] is not None else -1),
            row['club_name'].casefold(),row['club_id']))
        previous_points = None
        previous_rank = 0
        for position,entry in enumerate(season_standings,1):
            if entry['status']!='RANKED':
                break
            if previous_points is None or entry['total_points'] != previous_points:
                previous_rank = position
            entry['rank'] = previous_rank
            previous_points = entry['total_points']
        trades=[dict(x) for x in db.execute('SELECT * FROM trade ORDER BY id DESC LIMIT 40')]
    observatory={'status':'SOURCE_NOT_LOADED','votes':[], 'provenance':None}
    if pilot_csv and pilot_csv.is_file():
        # This is a manually transcribed aggregate, never a validated original.
        # Malformed local files must not crash the synthetic game endpoint.
        try:
            if pilot_csv.stat().st_size > 1_000_000:
                raise ValueError('Manual pilot file too large')
            with pilot_csv.open(encoding='utf-8',newline='') as handle:
                rows=list(csv.DictReader(handle))
            if not 0 < len(rows) <= 200:
                raise ValueError('Manual pilot row budget or empty file')
            votes=[]
            for row in rows:
                values=[int(row[name]) for name in ('yes','no','abstain')]
                if (any(v < 0 for v in values) or sum(values)>350
                        or not row['row_id'] or not row['event_date']):
                    raise ValueError('Invalid manual aggregate row')
                votes.append({'id':row['row_id'],'yes':values[0],'no':values[1],
                              'abstain':values[2],'date':row['event_date'],
                              'total':sum(values)})
            observatory={'status':'EXPLORATORY_MANUAL_AGGREGATE_NOT_VALIDATED', 'votes':votes,
                         'provenance':'Congreso, sesión plenaria 193 (2026-07-23); transcripción manual de recuentos; SIN DETALLE NOMINAL'}
        except (OSError, UnicodeError, ValueError, TypeError, KeyError, csv.Error):
            observatory={'status':'MANUAL_AGGREGATE_INVALID','votes':[], 'provenance':None}
    result = {'app':'Politics Fantasy League','version':'0.2.0-product-demo',
            'mode':DATA_PROVENANCE, 'authentication':'NONE_LOCAL_LOOPBACK_ONLY',
            'scoring_rule':DEMO_RULE.version,'roster_limit':MAX_OWNED,'lineup_size':LINEUP_SIZE,
            'figures':figures,'clubs':clubs,'rounds':rounds,'season_standings':season_standings,'trades':trades,
            'demo_clock': {'now':stamp(now), 'offset_seconds':clock_offset[0] if clock_offset else 0,
                           'simulated':bool(clock_offset and clock_offset[0])},
            'observatory':observatory,
            'research_status':'NO_REAL_INDIVIDUAL_PLAYER_SCORING_OR_PREDICTIONS'}
    from .insights import derive_all
    result['insights'] = derive_all(result)
    return result
