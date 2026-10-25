"""Strict offline adapters for *user supplied* Congreso Abierto CSV exports.

The website specifies field names, but this project has not downloaded and certified
its full corpus. Parsing is NOT proof that a CSV is official or that parliamentary
membership was historical. Avoid guessing original public-availability timestamps.
"""
from __future__ import annotations

import csv
import hashlib
import io
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

SOURCE_PAGE = 'https://congresoabierto.org/datos/'
ATTRIBUTION = ('Congreso Abierto (congresoabierto.org), '
               'a partir de datos oficiales del Congreso de los Diputados')
MAX_CSV_BYTES = 200 * 1024 * 1024
MANDATORY_INDIVIDUAL = frozenset(('votacion_id', 'fecha', 'diputado_id', 'grupo', 'voto'))
MANDATORY_AGGREGATE = frozenset(('id', 'fecha', 'si', 'no', 'abstencion', 'no_vota'))
_CHOICES = {'Sí':'YES', 'Si':'YES', 'SÍ':'YES', 'No':'NO',
            'Abstención':'ABSTAIN', 'Abstencion':'ABSTAIN', 'No vota':'NO_VOTE'}
_VOTE_ID = re.compile(r's\d+-v\d+\Z')


@dataclass(frozen=True)
class Provenance:
    source_page: str
    sha256: str
    input_bytes: int
    acquired_at: str
    provenance_status: str = 'LOCAL_BYTES_NOT_INDEPENDENTLY_CERTIFIED'
    declared_license: str = 'CC-BY-4.0--SEE_SOURCE_FOR_CURRENT_TERMS'


@dataclass(frozen=True)
class IndividualRow:
    vote_id: str
    day: date
    deputy_id: str
    group_label: str
    choice: str
    topic_label: str
    source_line: int


@dataclass(frozen=True)
class AggregateRow:
    vote_id: str
    day: date
    yes: int
    no: int
    abstain: int
    no_vote: int
    source_line: int


@dataclass(frozen=True)
class Parsed:
    provenance: Provenance
    rows: tuple[IndividualRow | AggregateRow, ...]
    data_kind: str
    group_at_vote_certified: bool = False


def _day(value: str) -> date:
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Date must be ISO YYYY-MM-DD')
    return date.fromisoformat(value)


def _id(value: str) -> str:
    value = value.strip()
    if not _VOTE_ID.fullmatch(value):
        raise ValueError('Unexpected vote identifier, review actual source schema')
    return value


def _count(value: str) -> int:
    if not re.fullmatch(r'\d+', value.strip()):
        raise ValueError('Counts must be nonnegative integers')
    return int(value)


def read_snapshot(path: Path, *, kind: str, acquired_at: datetime, max_rows: int=1_000_000) -> Parsed:
    """No network or inference of historical publication; accepts exact local bytes.

    Row limit is enforced independently of byte limit. Original byte hash is kept.
    """
    if kind not in ('individual', 'aggregate'):
        raise ValueError('Invalid table kind')
    if acquired_at.tzinfo is None or acquired_at.utcoffset() is None:
        raise ValueError('Acquisition timestamp must be offset-aware')
    if not isinstance(max_rows, int) or max_rows < 1:
        raise ValueError('Invalid row budget')
    path = Path(path)
    with path.open('rb') as stream:
        data = stream.read(MAX_CSV_BYTES + 1)
    if len(data) > MAX_CSV_BYTES:
        raise ValueError('Input exceeds the 200 MiB pilot cap')
    digest = hashlib.sha256(data).hexdigest()
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ValueError('File must be UTF-8 / UTF-8 BOM') from exc
    if '\x00' in text:
        raise ValueError('NUL byte in CSV')
    reader = csv.DictReader(io.StringIO(text, newline=''), restkey='__extra__')
    needed = MANDATORY_INDIVIDUAL if kind == 'individual' else MANDATORY_AGGREGATE
    headers = reader.fieldnames
    if not headers or len(headers) != len(set(headers)) or not needed.issubset(headers):
        raise ValueError(f'Missing or duplicated required {kind} CSV headers')
    seen = set()
    rows = []
    for ix, raw in enumerate(reader, 2):
        if ix - 1 > max_rows:
            raise ValueError('Input exceeds the row budget')
        if '__extra__' in raw or any(v is None for v in raw.values()):
            raise ValueError(f'Malformed columns at line {ix}')
        try:
            vote_id = _id(raw['votacion_id'] if kind == 'individual' else raw['id'])
            day = _day(raw['fecha'])
            if kind == 'individual':
                deputy_id = raw['diputado_id'].strip()
                group_label = raw['grupo'].strip()
                if not re.fullmatch(r'[\w.\-]{1,64}', deputy_id, re.UNICODE) or not group_label:
                    raise ValueError('Invalid deputy ID or missing group label')
                choice = _CHOICES.get(raw['voto'].strip())
                if choice is None:
                    raise ValueError('Unknown vote choice')
                key = (vote_id, deputy_id)
                item = IndividualRow(vote_id, day, deputy_id, group_label, choice,
                                     raw.get('temas', '').strip(), ix)
            else:
                key = vote_id
                item = AggregateRow(vote_id, day, _count(raw['si']), _count(raw['no']),
                                    _count(raw['abstencion']), _count(raw['no_vota']), ix)
            if key in seen:
                raise ValueError('Duplicate nominal row or aggregate vote identifier')
            seen.add(key)
            rows.append(item)
        except ValueError as exc:
            raise ValueError(f'Invalid {kind} CSV at line {ix}: {exc}') from exc
    if not rows:
        raise ValueError('No data rows')
    provenance = Provenance(SOURCE_PAGE, digest, len(data),
                            acquired_at.astimezone(timezone.utc).isoformat())
    return Parsed(provenance, tuple(rows), kind)


def summary_one(parsed: Parsed) -> dict:
    """Counts only, no personal names or rankings. All rates are descriptive."""
    if parsed.data_kind == 'individual':
        rows = parsed.rows
        by_vote = Counter(r.vote_id for r in rows)
        dist = Counter(r.choice for r in rows)
        return {'kind':'individual', 'n_rows':len(rows), 'n_votations':len(by_vote),
                'n_deputy_ids':len({r.deputy_id for r in rows}),
                'explicit_no_vote':dist['NO_VOTE'], 'expressed':sum(dist[x] for x in ('YES','NO','ABSTAIN')),
                'n_vote_dates':len({r.day for r in rows}),
                'n_group_labels':len({r.group_label for r in rows}),
                'group_at_vote_certified':False,
                'unknown_rows':'NOT_ESTIMABLE_WITHOUT_ROSTER',
                'status':'THIRD_PARTY_CSV_NOT_CERTIFIED'}
    return {'kind':'aggregate','n_rows':len(parsed.rows),
            'n_votations':len(parsed.rows),
            'sum_yes':sum(r.yes for r in parsed.rows),
            'sum_no':sum(r.no for r in parsed.rows),
            'sum_abstain':sum(r.abstain for r in parsed.rows),
            'sum_no_vote':sum(r.no_vote for r in parsed.rows),
            'individuals':'NOT_OBSERVED', 'status':'THIRD_PARTY_CSV_NOT_CERTIFIED'}
