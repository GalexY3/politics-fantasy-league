"""S9 durable registry of *closed, authored synthetic fixtures* only.

This deliberately does not accept user bytes, original documents, arbitrary
publishers, real entitlements, HTTP writes, or an independent denominator.
Stored source bytes are audited on EVERY read; only redacted descriptors and
synthetic typed, knowledge/valid-time bounded snapshots cross the HTTP layer.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sqlite3
from threading import RLock

from . import scientific_integration_lab as lab

SCHEMA_VERSION = 2
FAMILY_FILTERS = frozenset(("all", "PP04", "CHAIN", "CHRONICLE"))
VALID_DAYS = frozenset(("2026-09-11", "2026-09-15", "2026-10-10"))
PUBLICATION_FILTERS = frozenset(("as_of", "2026-09-19T12:00:00Z",
                                "2026-10-30T12:00:00Z"))
PURPOSE = "PUBLIC_AGGREGATE_DISPLAY"
FIXTURE_ID = "PFL_S9_CLOSED_AUTHOR_SYNTHETIC_V1"
SYNTHETIC_ONLY = "SYNTHETIC_LAB_ONLY"
_INITIALIZATION_LOCK = RLock()


class RegistryIntegrityError(RuntimeError):
    """A persisted fixture is incomplete, altered or scientifically conflicted."""


def _json(obj: object) -> str:
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,
                      separators=(",",":"),allow_nan=False)


def _sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _timestamp(value: str) -> datetime:
    if type(value) is not str or not value.endswith("Z"):
        raise RegistryIntegrityError("REGISTRY_TIMESTAMP_NOT_CANONICAL_UTC")
    try:
        parsed=datetime.fromisoformat(value[:-1]+"+00:00")
    except ValueError as exc:
        raise RegistryIntegrityError("REGISTRY_TIMESTAMP_INVALID") from exc
    if parsed.utcoffset().total_seconds()!=0 or parsed.isoformat(
            timespec="seconds").replace("+00:00","Z")!=value:
        raise RegistryIntegrityError("REGISTRY_TIMESTAMP_NOT_SECOND_PRECISION")
    return parsed


def _day(value: str) -> str:
    if type(value) is not str or len(value)!=10:
        raise RegistryIntegrityError("REGISTRY_DAY_INVALID")
    try:
        datetime.strptime(value,"%Y-%m-%d")
    except ValueError as exc:
        raise RegistryIntegrityError("REGISTRY_DAY_INVALID") from exc
    return value


def registry_path(game_db: Path) -> Path:
    """Dedicated database beside the local demo DB, never the account DB."""
    if not isinstance(game_db,Path):
        raise ValueError("S9_GAME_DB_PATH_REQUIRED")
    return game_db.parent/"scientific_registry_synthetic.sqlite3"


def _source(*, id: str, public: str | None, family: str, issuer: str,
            revision: int, prior: str | None, body: str,
            captured: str, published: str, quality: str,
            stage: str = "UNATTESTED") -> dict:
    data=body.encode("utf-8")
    if not data.startswith(b"SYNTHETIC"):
        raise RegistryIntegrityError("REGISTRY_FIXTURE_UNSAFE_PREFIX")
    descriptor=(f"S9 PUBLIC SYNTHETIC DESCRIPTOR\nID:{public}\n"
                f"FAMILY:{family}\nREVISION:{revision}\n"
                f"CAPTURE:{captured}\nPUBLICATION:{published}\n").encode("utf-8") if public else b""
    return dict(source_id=id,public_id=public,family=family,issuer=issuer,
                revision=revision,amendment_of=prior,source_bytes=data,
                source_sha256=_sha(data),captured_at=captured,
                first_public_known_at=published,first_public_at_real=None,
                purpose=PURPOSE,rights_for_purpose_admitted=0,
                issuer_authenticated_real=0,independent_denominator=None,
                quality_gate=quality,coverage_state="DISTRIBUTION_COVERAGE_UNATTESTED",
                provenance="AUTHORED_SYNTHETIC_FIXTURE_NOT_OFFICIAL",
                descriptor_bytes=descriptor,descriptor_sha256=_sha(descriptor) if public else None,
                stage_hint=stage)


def _closed_sources() -> list[dict]:
    chronology=lab._bitemporal_fixture()
    chain=lab._typed_institutional_chain_fixture()
    assets=lab._assets()
    early="2026-09-19T12:00:00Z"
    late=lab.LATE_PUBLIC
    rows=[
        _source(id=chronology["sources"][0]["source_id"],public="S9:PUBLIC_01",
                family="CHRONICLE",issuer=chronology["issuer"],revision=1,prior=None,
                body=chronology["sources"][0]["text"],
                captured=chronology["sources"][0]["captured_at"],published=early,
                quality="INTERNAL_CHRONICLE_SHA_AND_REVISION_CHECK_ONLY"),
        _source(id=chain["sources"][0]["source_id"],public="S9:PUBLIC_02",
                family="CHAIN",issuer=chain["issuer"],revision=1,prior=None,
                body=chain["sources"][0]["text"],
                captured=chain["sources"][0]["captured_at"],published=early,
                quality="INTERNAL_CHAIN_SHA_AND_TYPED_KEY_CHECK_ONLY"),
        _source(id=chronology["sources"][1]["source_id"],public="S9:PUBLIC_03",
                family="CHRONICLE",issuer=chronology["issuer"],revision=2,
                prior=chronology["sources"][0]["source_id"],
                body=chronology["sources"][1]["text"],
                captured=chronology["sources"][1]["captured_at"],published=late,
                quality="INTERNAL_CHRONICLE_SHA_AND_REVISION_CHECK_ONLY"),
        _source(id=chain["sources"][1]["source_id"],public="S9:PUBLIC_04",
                family="CHAIN",issuer=chain["issuer"],revision=2,
                prior=chain["sources"][0]["source_id"],
                body=chain["sources"][1]["text"],
                captured=chain["sources"][1]["captured_at"],published=late,
                quality="INTERNAL_CHAIN_SHA_AND_TYPED_KEY_CHECK_ONLY"),
        _source(id=assets[0]["id"],public="S9:PUBLIC_05",
                family="PP04",issuer="SYN:PP04_PARSER",revision=1,prior=None,
                body=assets[0]["text"],captured=lab.LATE_CAPTURE,published=late,
                quality="SOURCE_LOCAL_PAN_PARSER_FIXTURE_NOT_OUTCOME"),
        _source(id=assets[1]["id"],public="S9:PUBLIC_06",
                family="PP04",issuer="SYN:PP04_PARSER",revision=1,prior=None,
                body=assets[1]["text"],captured=lab.LATE_CAPTURE,published=late,
                quality="SOURCE_LOCAL_IAEN_PARSER_FIXTURE_NOT_OUTCOME"),
        # A documented stage belongs to the existing synthetic procedural
        # test universe. It is NEVER a new public distribution or true N.
        _source(id="SYN:S9_INTERNAL_STAGE",public=None,
                family="STAGE",issuer="SYN:S9_LOCAL_STAGE",revision=1,prior=None,
                body="SYNTHETIC_STAGE_DOCUMENT\n",captured=lab.LATE_CAPTURE,
                published=late,quality="INTERNAL_STAGED_PROCEDURE_FIXTURE_ONLY",
                stage="NON_PUBLIC_EXPLICIT_SYNTHETIC_NEGATIVE_WITNESS"),
    ]
    if (rows[4]["source_sha256"]!=assets[0]["sha256"]
            or rows[5]["source_sha256"]!=assets[1]["sha256"]
            or rows[-1]["source_sha256"]!=lab._sha(b"SYNTHETIC_STAGE_DOCUMENT\n")):
        raise RegistryIntegrityError("REGISTRY_SEED_SOURCE_PARITY_FAILED")
    return rows


def _fact(fact_id: str, source_id: str, issuer: str, kind: str, local_key: str,
          revision: int, amendment_of: str | None, valid_from: str,
          observed_at: str, *, valid_to: str | None = None,
          state: str = "DOCUMENTED_SYNTHETIC", target: str | None = None) -> dict:
    return dict(fact_id=fact_id,source_id=source_id,issuer=issuer,kind=kind,
                source_local_key=local_key,revision=revision,amendment_of=amendment_of,
                valid_from=valid_from,valid_to=valid_to,observed_at=observed_at,
                evidentiary_state=state,target_local_key=target,
                official_crosswalk_verified=0)


def _closed_facts() -> list[dict]:
    c1,c2="SYN:CHAIN_V1","SYN:CHAIN_V2"
    h1,h2="SYN:CHRONICLE_V1","SYN:CHRONICLE_V2"
    early,late=lab.EARLY_CAPTURE,lab.LATE_CAPTURE
    return [
        _fact("S9:C:ACTOR",c1,"SYN:CHAIN","ACTOR","A",1,None,"2026-09-05",early),
        _fact("S9:C:ORG",c1,"SYN:CHAIN","ORGANIZATION","O",1,None,"2026-09-05",early),
        _fact("S9:C:PROCESS",c1,"SYN:CHAIN","PROCESS","P1",1,None,"2026-09-05",early,state="ENTRY_DOCUMENTED"),
        _fact("S9:C:COMM_V1",c1,"SYN:CHAIN","COMMUNICATION","C1",1,None,"2026-09-10",early,
              state="COMMUNICATION_DOCUMENTED",target="PROCESS:P1"),
        _fact("S9:C:COMM_V2",c2,"SYN:CHAIN","COMMUNICATION","C1",2,"S9:C:COMM_V1","2026-09-10",late,
              state="COMMUNICATION_AMENDED",target="PROCESS:P1"),
        _fact("S9:C:DECISION",c2,"SYN:CHAIN","DECISION","D1",1,None,"2026-09-14",late,
              state="EXPLICIT_APPROVAL_DOCUMENTED_SYNTHETIC",target="PROCESS:P1"),
        _fact("S9:C:PENDING",c1,"SYN:CHAIN","EPISODE_STAGE","P1:PENDING",1,None,"2026-09-12",early,
              state="PENDING_NOT_NEGATIVE",target="PROCESS:P1"),
        _fact("S9:C:APPROVED",c2,"SYN:CHAIN","EPISODE_STAGE","P1:APPROVED",1,None,"2026-09-14",late,
              state="EXPLICIT_APPROVAL",target="PROCESS:P1"),
        _fact("S9:H:ACTOR",h1,"SYN:CHRONICLE","ACTOR","A",1,None,"2026-09-01",early),
        _fact("S9:H:ORG",h1,"SYN:CHRONICLE","ORGANIZATION","O",1,None,"2026-09-01",early),
        _fact("S9:H:ROLE_V1",h1,"SYN:CHRONICLE","ROLE","OFFICE_ROLE",1,None,"2026-09-01",early,
              valid_to="2026-10-01",state="ROLE_DOCUMENTED",target="ORGANIZATION:O"),
        _fact("S9:H:ROLE_V2",h2,"SYN:CHRONICLE","ROLE","OFFICE_ROLE",2,"S9:H:ROLE_V1","2026-10-01",late,
              state="ROLE_REVISED",target="ORGANIZATION:O"),
        _fact("S9:H:EVENT_V1",h1,"SYN:CHRONICLE","EVENT","INITIATIVE:FILE_1",1,None,"2026-09-10",early,
              state="EVENT_DOCUMENTED_NOT_TERMINAL"),
        _fact("S9:H:EVENT_V2",h2,"SYN:CHRONICLE","EVENT","INITIATIVE:FILE_1",2,"S9:H:EVENT_V1","2026-09-10",late,
              state="EVENT_REVISED_NOT_SECOND_EVENT"),
        _fact("S9:P:APPROVED", "SYNTHETIC:IAEN24","SYN:PP04_PARSER","PP04_STATEMENT","INCLUIDAS:APPROVED",1,None,"2026-09-10",late,
              state="INCLUIDAS_PLANNED_APPROVED_SOURCE_LOCAL_ONLY"),
        _fact("S9:P:PENDING", "SYNTHETIC:IAEN24","SYN:PP04_PARSER","PP04_STATEMENT","INCLUIDAS:PENDING",1,None,"2026-09-10",late,
              state="INCLUIDAS_PENDING_NOT_NEGATIVE"),
        _fact("S9:P:UNPLANNED_1", "SYNTHETIC:IAEN24","SYN:PP04_PARSER","PP04_STATEMENT","NO_INCLUIDAS:1",1,None,"2026-09-10",late,
              state="NO_INCLUIDAS_NOT_NEGATIVE_NOT_IN_COHORT"),
        _fact("S9:P:UNPLANNED_2", "SYNTHETIC:IAEN24","SYN:PP04_PARSER","PP04_STATEMENT","NO_INCLUIDAS:2",1,None,"2026-09-10",late,
              state="NO_INCLUIDAS_NOT_NEGATIVE_NOT_IN_COHORT"),
        _fact("S9:S:ENTRY", "SYN:S9_INTERNAL_STAGE","SYN:S9_LOCAL_STAGE","EPISODE_STAGE","S9_P2:ENTRY",1,None,"2026-09-02",late,
              state="ENTRY_DOCUMENTED_SYNTHETIC"),
        _fact("S9:S:INADMITTED", "SYN:S9_INTERNAL_STAGE","SYN:S9_LOCAL_STAGE","EPISODE_STAGE","S9_P2:INADMITTED",1,None,"2026-09-11",late,
              state="EXPLICIT_INADMITTED_SYNTHETIC_NOT_CENSOR"),
    ]


def _edge(edge_id: str, source_id: str, issuer: str,
          from_kind: str, from_local: str, to_kind: str, to_local: str,
          relation: str, valid_from: str, observed_at: str) -> dict:
    return dict(edge_id=edge_id,source_id=source_id,issuer=issuer,
                from_kind=from_kind,from_local=from_local,to_kind=to_kind,
                to_local=to_local,relation=relation,valid_from=valid_from,
                observed_at=observed_at,official_crosswalk_verified=0)


def _closed_edges() -> list[dict]:
    early,late=lab.EARLY_CAPTURE,lab.LATE_CAPTURE
    return [
        _edge("S9:E:C:ACTOR_ORG","SYN:CHAIN_V1","SYN:CHAIN", "ACTOR","A","ORGANIZATION","O", "ASSOCIATED_WITH_SYNTHETIC", "2026-09-05",early),
        _edge("S9:E:C:ACTOR_COMM","SYN:CHAIN_V1","SYN:CHAIN", "ACTOR","A","COMMUNICATION","C1", "AUTHORED_SYNTHETIC", "2026-09-10",early),
        _edge("S9:E:C:COMM_PROCESS","SYN:CHAIN_V1","SYN:CHAIN", "COMMUNICATION","C1","PROCESS","P1", "REFERS_TO_PROCESS_SYNTHETIC", "2026-09-10",early),
        _edge("S9:E:C:DEC_PROCESS","SYN:CHAIN_V2","SYN:CHAIN", "DECISION","D1","PROCESS","P1", "TERMINAL_STAGE_DOCUMENTED_SYNTHETIC", "2026-09-14",late),
        _edge("S9:E:H:ACTOR_ORG","SYN:CHRONICLE_V1","SYN:CHRONICLE", "ACTOR","A","ORGANIZATION","O", "FIXTURE_ROLE_RELATION", "2026-09-01",early),
        _edge("S9:E:H:ROLE_ORG","SYN:CHRONICLE_V1","SYN:CHRONICLE", "ROLE","OFFICE_ROLE","ORGANIZATION","O", "DOCUMENTS_OFFICE_ROLE", "2026-09-01",early),
    ]


SOURCES_COLUMNS=("source_id","public_id","family","issuer","revision",
    "amendment_of","source_bytes","source_sha256","captured_at",
    "first_public_known_at","first_public_at_real","purpose",
    "rights_for_purpose_admitted","issuer_authenticated_real",
    "independent_denominator","quality_gate","coverage_state","provenance",
    "descriptor_bytes","descriptor_sha256","stage_hint")
FACT_COLUMNS=("fact_id","source_id","issuer","kind","source_local_key",
    "revision","amendment_of","valid_from","valid_to","observed_at",
    "evidentiary_state","target_local_key","official_crosswalk_verified")
EDGE_COLUMNS=("edge_id","source_id","issuer","from_kind","from_local",
    "to_kind","to_local","relation","valid_from","observed_at",
    "official_crosswalk_verified")
_TRIGGER_DEFINITIONS={
    "registry_distribution_immutable_update":("UPDATE","distribution","IMMUTABLE_SOURCE_REVISION"),
    "registry_distribution_immutable_delete":("DELETE","distribution","IMMUTABLE_SOURCE_REVISION"),
    "registry_fact_immutable_update":("UPDATE","typed_fact","IMMUTABLE_TYPED_RECORD"),
    "registry_fact_immutable_delete":("DELETE","typed_fact","IMMUTABLE_TYPED_RECORD"),
    "registry_edge_immutable_update":("UPDATE","typed_edge","IMMUTABLE_TYPED_EDGE"),
    "registry_edge_immutable_delete":("DELETE","typed_edge","IMMUTABLE_TYPED_EDGE"),
}


@contextmanager
def _connect(path: Path):
    db=sqlite3.connect(str(path),timeout=4,isolation_level=None)
    db.row_factory=sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=4000")
    try:
        yield db
    finally:
        db.close()


def _execute_ddl_atomically(db: sqlite3.Connection, statements: str) -> None:
    """Unlike sqlite3.executescript, do not implicitly COMMIT the caller's TX."""
    buffer=""
    for line in statements.splitlines(keepends=True):
        buffer+=line
        if sqlite3.complete_statement(buffer):
            db.execute(buffer.strip())
            buffer=""
    if buffer.strip():
        raise RegistryIntegrityError("REGISTRY_DDL_INCOMPLETE")


def _migration_v1(db: sqlite3.Connection) -> None:
    _execute_ddl_atomically(db,"""
        CREATE TABLE registry_meta (
            id INTEGER PRIMARY KEY CHECK(id=1),
            fixture_id TEXT NOT NULL,
            manifest_sha256 TEXT NOT NULL,
            created_at TEXT NOT NULL,
            admission TEXT NOT NULL CHECK(admission='STOP_R5')
        );
        CREATE TABLE distribution (
            source_id TEXT PRIMARY KEY,
            public_id TEXT UNIQUE,
            family TEXT NOT NULL CHECK(family IN('PP04','CHAIN','CHRONICLE','STAGE')),
            issuer TEXT NOT NULL,
            revision INTEGER NOT NULL CHECK(revision>=1),
            amendment_of TEXT REFERENCES distribution(source_id),
            source_bytes BLOB NOT NULL,
            source_sha256 TEXT NOT NULL,
            captured_at TEXT NOT NULL,
            first_public_known_at TEXT NOT NULL,
            first_public_at_real TEXT CHECK(first_public_at_real IS NULL),
            purpose TEXT NOT NULL CHECK(purpose='PUBLIC_AGGREGATE_DISPLAY'),
            rights_for_purpose_admitted INTEGER NOT NULL DEFAULT 0 CHECK(rights_for_purpose_admitted=0),
            issuer_authenticated_real INTEGER NOT NULL DEFAULT 0 CHECK(issuer_authenticated_real=0),
            independent_denominator INTEGER CHECK(independent_denominator IS NULL),
            quality_gate TEXT NOT NULL,
            coverage_state TEXT NOT NULL CHECK(coverage_state='DISTRIBUTION_COVERAGE_UNATTESTED'),
            provenance TEXT NOT NULL CHECK(provenance='AUTHORED_SYNTHETIC_FIXTURE_NOT_OFFICIAL'),
            descriptor_bytes BLOB NOT NULL,
            descriptor_sha256 TEXT,
            stage_hint TEXT NOT NULL,
            CHECK((public_id IS NULL AND descriptor_sha256 IS NULL AND length(descriptor_bytes)=0)
               OR (public_id IS NOT NULL AND descriptor_sha256 IS NOT NULL AND length(descriptor_bytes)>0))
        );
        CREATE INDEX idx_registry_distribution_time
          ON distribution(captured_at,first_public_known_at,family);
    """)
    db.execute("PRAGMA user_version=1")


def _migration_v2(db: sqlite3.Connection) -> None:
    _execute_ddl_atomically(db,"""
        CREATE TABLE typed_fact (
            fact_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL REFERENCES distribution(source_id),
            issuer TEXT NOT NULL,
            kind TEXT NOT NULL CHECK(kind IN('ACTOR','ORGANIZATION','ROLE','EVENT',
                'COMMUNICATION','DECISION','PROCESS','EPISODE_STAGE','PP04_STATEMENT')),
            source_local_key TEXT NOT NULL,
            revision INTEGER NOT NULL CHECK(revision>=1),
            amendment_of TEXT REFERENCES typed_fact(fact_id),
            valid_from TEXT NOT NULL,
            valid_to TEXT,
            observed_at TEXT NOT NULL,
            evidentiary_state TEXT NOT NULL,
            target_local_key TEXT,
            official_crosswalk_verified INTEGER NOT NULL DEFAULT 0 CHECK(official_crosswalk_verified=0)
        );
        CREATE INDEX idx_registry_fact_bitemporal
          ON typed_fact(issuer,kind,source_local_key,observed_at,valid_from);
        CREATE TABLE typed_edge (
            edge_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL REFERENCES distribution(source_id),
            issuer TEXT NOT NULL,
            from_kind TEXT NOT NULL,
            from_local TEXT NOT NULL,
            to_kind TEXT NOT NULL,
            to_local TEXT NOT NULL,
            relation TEXT NOT NULL,
            valid_from TEXT NOT NULL,
            observed_at TEXT NOT NULL,
            official_crosswalk_verified INTEGER NOT NULL DEFAULT 0 CHECK(official_crosswalk_verified=0)
        );
        CREATE TABLE schema_history (
            version INTEGER PRIMARY KEY,
            migration TEXT NOT NULL,
            applied_at_fixture TEXT NOT NULL
        );
        INSERT INTO schema_history VALUES(1,'REGISTRY_SOURCES_BLOB_SHA','2026-11-01T12:00:00Z');
        INSERT INTO schema_history VALUES(2,'REGISTRY_SOURCE_LOCAL_TYPED_EDGES','2026-11-01T12:00:00Z');
        CREATE TRIGGER registry_distribution_immutable_update BEFORE UPDATE ON distribution
          BEGIN SELECT RAISE(ABORT,'IMMUTABLE_SOURCE_REVISION'); END;
        CREATE TRIGGER registry_distribution_immutable_delete BEFORE DELETE ON distribution
          BEGIN SELECT RAISE(ABORT,'IMMUTABLE_SOURCE_REVISION'); END;
        CREATE TRIGGER registry_fact_immutable_update BEFORE UPDATE ON typed_fact
          BEGIN SELECT RAISE(ABORT,'IMMUTABLE_TYPED_RECORD'); END;
        CREATE TRIGGER registry_fact_immutable_delete BEFORE DELETE ON typed_fact
          BEGIN SELECT RAISE(ABORT,'IMMUTABLE_TYPED_RECORD'); END;
        CREATE TRIGGER registry_edge_immutable_update BEFORE UPDATE ON typed_edge
          BEGIN SELECT RAISE(ABORT,'IMMUTABLE_TYPED_EDGE'); END;
        CREATE TRIGGER registry_edge_immutable_delete BEFORE DELETE ON typed_edge
          BEGIN SELECT RAISE(ABORT,'IMMUTABLE_TYPED_EDGE'); END;
    """)
    db.execute("PRAGMA user_version=2")


def _manifest_hash() -> str:
    def public_source(s:dict) -> dict:
        return {k:(s[k].hex() if isinstance(s[k],bytes) else s[k])
                for k in SOURCES_COLUMNS}
    return _sha(_json({"sources":[public_source(s) for s in _closed_sources()],
                       "facts":_closed_facts(),"edges":_closed_edges()}).encode("utf-8"))


def _schema_sha256(db: sqlite3.Connection) -> str:
    """Check constraints, columns, indexes AND trigger SQL, not user_version alone."""
    objects=[tuple(row) for row in db.execute(
        "SELECT type,name,tbl_name,sql FROM sqlite_master "
        "WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name")]
    return _sha(_json(objects).encode("utf-8"))


@lru_cache(maxsize=1)
def _expected_schema_sha256() -> str:
    with sqlite3.connect(":memory:",isolation_level=None) as db:
        db.execute("BEGIN IMMEDIATE")
        _migration_v1(db)
        _migration_v2(db)
        result=_schema_sha256(db)
        db.rollback()
        return result


def _migrate(db: sqlite3.Connection) -> None:
    version=db.execute("PRAGMA user_version").fetchone()[0]
    if version not in (0,1,2):
        raise RegistryIntegrityError("REGISTRY_UNKNOWN_SCHEMA_VERSION")
    if version==0:
        if db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone()[0]:
            raise RegistryIntegrityError("REGISTRY_UNVERSIONED_SCHEMA_NOT_TRUSTED")
        _migration_v1(db)
        version=1
    if version==1:
        _migration_v2(db)
    if db.execute("PRAGMA user_version").fetchone()[0]!=SCHEMA_VERSION:
        raise RegistryIntegrityError("REGISTRY_MIGRATION_DIVERGENCE")


def _insert_rows(db:sqlite3.Connection,table:str,columns:tuple,rows:list[dict]) -> None:
    fields=",".join(columns)
    placeholders=",".join("?" for _ in columns)
    db.executemany(f"INSERT INTO {table}({fields}) VALUES({placeholders})",
                   [[r[column] for column in columns] for r in rows])


def _seed(db:sqlite3.Connection) -> None:
    sources=_closed_sources()
    facts=_closed_facts()
    edges=_closed_edges()
    digest=_manifest_hash()
    db.execute("INSERT INTO registry_meta VALUES(1,?,?,?,?)",
               (FIXTURE_ID,digest,"2026-11-01T12:00:00Z","STOP_R5"))
    _insert_rows(db,"distribution",SOURCES_COLUMNS,sources)
    _insert_rows(db,"typed_fact",FACT_COLUMNS,facts)
    _insert_rows(db,"typed_edge",EDGE_COLUMNS,edges)


def _actual_rows(db:sqlite3.Connection,table:str,columns:tuple) -> list[dict]:
    selected=",".join(columns)
    rows=db.execute(f"SELECT {selected} FROM {table} ORDER BY 1").fetchall()
    return [dict(row) for row in rows]


def _audit(db:sqlite3.Connection) -> tuple[list[dict],list[dict],list[dict]]:
    if db.execute("PRAGMA user_version").fetchone()[0]!=SCHEMA_VERSION:
        raise RegistryIntegrityError("REGISTRY_SCHEMA_VERSION_MISMATCH")
    if _schema_sha256(db)!=_expected_schema_sha256():
        raise RegistryIntegrityError("REGISTRY_SCHEMA_DDL_HASH_DIVERGENCE")
    meta=db.execute("SELECT * FROM registry_meta WHERE id=1").fetchone()
    if (meta is None or meta["fixture_id"]!=FIXTURE_ID or
            meta["manifest_sha256"]!=_manifest_hash() or
            meta["admission"]!="STOP_R5"):
        raise RegistryIntegrityError("REGISTRY_MANIFEST_OR_ADMISSION_DIVERGENCE")
    versions=[tuple(r) for r in db.execute("SELECT * FROM schema_history ORDER BY version")]
    if versions!=[(1,"REGISTRY_SOURCES_BLOB_SHA","2026-11-01T12:00:00Z"),
                  (2,"REGISTRY_SOURCE_LOCAL_TYPED_EDGES","2026-11-01T12:00:00Z")]:
        raise RegistryIntegrityError("REGISTRY_SCHEMA_HISTORY_CORRUPTED")
    triggers={r[0]:r[1] for r in db.execute(
        "SELECT name,sql FROM sqlite_master WHERE type='trigger'")}
    if set(triggers)!=set(_TRIGGER_DEFINITIONS):
        raise RegistryIntegrityError("REGISTRY_IMMUTABILITY_TRIGGER_MISSING_OR_ADDED")
    for name,(action,table,error) in _TRIGGER_DEFINITIONS.items():
        expected=f"CREATE TRIGGER {name} BEFORE {action} ON {table} " \
                 f"BEGIN SELECT RAISE(ABORT,'{error}'); END"
        canonical=lambda value: " ".join(value.strip().rstrip(";").split()).lower()
        if canonical(triggers[name])!=canonical(expected):
            raise RegistryIntegrityError("REGISTRY_IMMUTABILITY_TRIGGER_BODY_CHANGED")
    # Per-row bytes receipt checked independently before content comparison.
    actual_s=_actual_rows(db,"distribution",SOURCES_COLUMNS)
    expected_s=sorted(_closed_sources(),key=lambda x:x["source_id"])
    if len(actual_s)!=len(expected_s):
        raise RegistryIntegrityError("REGISTRY_SOURCE_SET_INCOMPLETE")
    for source,expected in zip(actual_s,expected_s):
        if (type(source["source_bytes"]) is not bytes or
                _sha(source["source_bytes"])!=source["source_sha256"] or
                (source["public_id"] is not None and
                 _sha(source["descriptor_bytes"])!=source["descriptor_sha256"])):
            raise RegistryIntegrityError("REGISTRY_BYTES_SHA_TAMPER")
        _timestamp(source["first_public_known_at"])
        _timestamp(source["captured_at"])
        if _timestamp(source["first_public_known_at"])>_timestamp(source["captured_at"]):
            raise RegistryIntegrityError("REGISTRY_RETRO_FIRST_PUBLIC_CONTRADICTION")
        if source!=expected:
            raise RegistryIntegrityError("REGISTRY_UNAUTHORIZED_SOURCE_REVISION_OR_RIGHTS")
    actual_f=_actual_rows(db,"typed_fact",FACT_COLUMNS)
    if actual_f!=sorted(_closed_facts(),key=lambda x:x["fact_id"]):
        raise RegistryIntegrityError("REGISTRY_TYPED_KEY_OR_AMENDMENT_DIVERGENCE")
    actual_e=_actual_rows(db,"typed_edge",EDGE_COLUMNS)
    if actual_e!=sorted(_closed_edges(),key=lambda x:x["edge_id"]):
        raise RegistryIntegrityError("REGISTRY_SOURCE_LOCAL_CROSSWALK_DIVERGENCE")
    registered={s["source_id"]:s for s in actual_s}
    indexed={(f["issuer"],f["kind"],f["source_local_key"])
             for f in actual_f}
    facts_by_id={f["fact_id"]:f for f in actual_f}
    for fact in actual_f:
        source=registered[fact["source_id"]]
        _day(fact["valid_from"])
        if fact["valid_to"] is not None and _day(fact["valid_to"])<=fact["valid_from"]:
            raise RegistryIntegrityError("REGISTRY_INVALID_VALID_INTERVAL")
        if (source["issuer"]!=fact["issuer"] or
                _timestamp(fact["observed_at"])<_timestamp(source["captured_at"])):
            raise RegistryIntegrityError("REGISTRY_FACT_ISSUER_OR_CAPTURE_CONTRADICTION")
        if fact["amendment_of"]:
            predecessor=facts_by_id.get(fact["amendment_of"])
            if (predecessor is None or
                    (predecessor["issuer"],predecessor["kind"],predecessor["source_local_key"])!=
                    (fact["issuer"],fact["kind"],fact["source_local_key"]) or
                    predecessor["revision"]>=fact["revision"] or
                    _timestamp(predecessor["observed_at"])>=_timestamp(fact["observed_at"])):
                raise RegistryIntegrityError("REGISTRY_CONTRADICTORY_AMENDMENT")
    for edge in actual_e:
        source=registered[edge["source_id"]]
        if source["issuer"]!=edge["issuer"]:
            raise RegistryIntegrityError("REGISTRY_EDGE_CROSS_ISSUER")
        for kind,key in ((edge["from_kind"],edge["from_local"]),
                         (edge["to_kind"],edge["to_local"])):
            if (edge["issuer"],kind,key) not in indexed:
                raise RegistryIntegrityError("REGISTRY_EDGE_UNKNOWN_TYPED_KEY")
        _day(edge["valid_from"])
    return actual_s,actual_f,actual_e


def seed_registry(path:Path) -> None:
    """Idempotent atomic replay, serialized within a Python server process."""
    with _INITIALIZATION_LOCK:
        _seed_registry_locked(path)


def _seed_registry_locked(path:Path) -> None:
    """Migrate once; do not rewrite or silently heal a corrupted fixture."""
    path=Path(path)
    existed=path.exists()
    if existed and path.stat().st_size==0:
        raise RegistryIntegrityError("REGISTRY_CORRUPT_EMPTY_EXISTING_DATABASE")
    path.parent.mkdir(parents=True,exist_ok=True)
    try:
        with _connect(path) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                before=db.execute("PRAGMA user_version").fetchone()[0]
                _migrate(db)
                present=db.execute("SELECT count(*) FROM registry_meta").fetchone()[0]
                if present==0:
                    if any(db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                           for table in ("distribution","typed_fact","typed_edge")):
                        raise RegistryIntegrityError("REGISTRY_PARTIAL_SEED_NOT_REPAIRED")
                    _seed(db)
                elif before==1 and present==1:
                    # The previous version already contained immutable source
                    # bytes. Migrate their schema IN PLACE, preserving all
                    # original bytes/revisions and adding only typed tables.
                    # Any incomplete/tampered v1 data must fail, never reset.
                    previous=_actual_rows(db,"distribution",SOURCES_COLUMNS)
                    if (previous!=sorted(_closed_sources(),key=lambda x:x["source_id"])
                            or any(db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                                   for table in ("typed_fact","typed_edge"))):
                        raise RegistryIntegrityError("REGISTRY_V1_MIGRATION_SOURCE_MISMATCH")
                    meta=db.execute("SELECT * FROM registry_meta").fetchone()
                    if (meta["fixture_id"]!=FIXTURE_ID or
                            meta["manifest_sha256"]!=_manifest_hash() or
                            meta["admission"]!="STOP_R5"):
                        raise RegistryIntegrityError("REGISTRY_V1_MIGRATION_MANIFEST_MISMATCH")
                    _insert_rows(db,"typed_fact",FACT_COLUMNS,_closed_facts())
                    _insert_rows(db,"typed_edge",EDGE_COLUMNS,_closed_edges())
                _audit(db)
                db.commit()
            except Exception:
                db.rollback()
                raise
    except sqlite3.DatabaseError as exc:
        raise RegistryIntegrityError("REGISTRY_SQLITE_INTEGRITY_FAILURE") from exc


def _visible(source:dict,as_of:str,published_until:str) -> bool:
    return (source["captured_at"]<=as_of and
            source["first_public_known_at"]<=as_of and
            source["first_public_known_at"]<=published_until)


def _snapshot(*,sources:list[dict],facts:list[dict],edges:list[dict],
              as_of:str,valid_at:str,family:str,published_until:str) -> dict:
    source_set={s["source_id"] for s in sources if _visible(s,as_of,published_until)}
    source_issuer={s["source_id"]:s["issuer"] for s in sources}
    visible_facts=[f for f in facts if f["source_id"] in source_set and
                   f["observed_at"]<=as_of and f["valid_from"]<=valid_at and
                   (f["valid_to"] is None or valid_at<f["valid_to"])]
    chosen_issuer=(None if family=="all" else {
        "PP04":"SYN:PP04_PARSER","CHAIN":"SYN:CHAIN",
        "CHRONICLE":"SYN:CHRONICLE"}[family])
    visible_facts=[f for f in visible_facts if chosen_issuer is None or
                   f["issuer"]==chosen_issuer]
    visible_edges=[e for e in edges if e["source_id"] in source_set and
                   e["observed_at"]<=as_of and e["valid_from"]<=valid_at and
                   (chosen_issuer is None or e["issuer"]==chosen_issuer)]
    by_issuer:dict[str,list[dict]]={}
    for fact in visible_facts:
        by_issuer.setdefault(fact["issuer"],[]).append(fact)

    def render_graph(issuer:str, label:str) -> dict:
        all_f=by_issuer.get(issuer,[])
        entities={}
        for f in all_f:
            if f["kind"] in ("ACTOR","ORGANIZATION","COMMUNICATION","DECISION",
                             "PROCESS","ROLE","EVENT"):
                name=f["kind"]+":"+f["source_local_key"]
                # A documentary amendment remains ONE logical node.
                if name not in entities or f["revision"]>entities[name]["revision"]:
                    entities[name]=f
        sorted_keys=sorted(entities)
        labels={"ACTOR":"Actor ficticio", "ORGANIZATION":"Organización ficticia",
                "COMMUNICATION":"Comunicación ficticia",
                "DECISION":"Decisión ficticia", "PROCESS":"Proceso ficticio",
                "ROLE":"Rol documental ficticio", "EVENT":"Evento documental ficticio"}
        nodes=[]
        for i,key in enumerate(sorted_keys,1):
            kind=entities[key]["kind"]
            nodes.append({"id":f"S9:{label}:NODE_{i:02d}","kind":kind,
                          "label":labels[kind],"documentary_revision_count":sum(
                              x["kind"]==kind and x["source_local_key"]==entities[key]["source_local_key"]
                              for x in all_f)})
        node_ids={key:node["id"] for key,node in zip(sorted_keys,nodes)}
        links=[]
        for e in visible_edges:
            if e["issuer"]!=issuer:
                continue
            frm=e["from_kind"]+":"+e["from_local"]
            to=e["to_kind"]+":"+e["to_local"]
            if frm in node_ids and to in node_ids:
                links.append({"from":node_ids[frm],"to":node_ids[to],
                              "kind":e["relation"]})
        return {"nodes":nodes,"edges":links,"node_count":len(nodes),
                "edge_count":len(links),"issuer":"FICTIONAL_"+label,
                "amendments_count_as_new_people_or_decisions":False}

    chain=render_graph("SYN:CHAIN","CHAIN") if family in ("all","CHAIN") else None
    chronicle=render_graph("SYN:CHRONICLE","CHRONICLE") if family in ("all","CHRONICLE") else None
    chain_states=[f["evidentiary_state"] for f in by_issuer.get("SYN:CHAIN",[])
                  if f["kind"]=="EPISODE_STAGE"]
    stage_states=[f["evidentiary_state"] for f in by_issuer.get("SYN:S9_LOCAL_STAGE",[])
                  if f["kind"]=="EPISODE_STAGE"]
    all_stages=chain_states+stage_states
    if ("EXPLICIT_APPROVAL" in all_stages and "PENDING_NOT_NEGATIVE" not in all_stages):
        # A late approval may coexist with an earlier documented pending;
        # no state is made negative by lack of a terminal at another cut.
        raise RegistryIntegrityError("REGISTRY_EPISODE_STAGE_HISTORY_CONFLICT")
    if "EXPLICIT_APPROVAL" in chain_states:
        process_state="APPROVED_AS_OF_SYNTHETIC_EVIDENCE"
    elif "PENDING_NOT_NEGATIVE" in chain_states:
        process_state="PENDING_NOT_NEGATIVE"
    elif any(f["kind"]=="PROCESS" for f in by_issuer.get("SYN:CHAIN",[])):
        process_state="UNKNOWN_FOLLOWUP_NOT_NEGATIVE"
    else:
        process_state="NOT_YET_DOCUMENTED"
    pp04=[f["evidentiary_state"] for f in by_issuer.get("SYN:PP04_PARSER",[])
          if f["kind"]=="PP04_STATEMENT"]
    return {
        "knowledge_as_of":as_of,"valid_at":valid_at,
        "graph": {"chain":chain,"chronicle":chronicle,
                  "cross_issuer_links_created":False},
        "episodes": {
            "chain_process_state":process_state,
            "explicit_negative_documented":sum(s=="EXPLICIT_INADMITTED_SYNTHETIC_NOT_CENSOR"
                                                for s in all_stages),
            "explicit_approval_documented":int("EXPLICIT_APPROVAL" in all_stages),
            "pending_documented_not_negative":int("PENDING_NOT_NEGATIVE" in all_stages),
            "right_censor_independently_attested":False,
            "unobserved_is_negative":False,
            "source_local_all_received_denominator":None,
        },
        "pp04": {"included_planned_approved":sum(x=="INCLUIDAS_PLANNED_APPROVED_SOURCE_LOCAL_ONLY" for x in pp04),
                 "included_pending_not_negative":sum(x=="INCLUIDAS_PENDING_NOT_NEGATIVE" for x in pp04),
                 "not_included_source_local_not_negative":sum(x=="NO_INCLUIDAS_NOT_NEGATIVE_NOT_IN_COHORT" for x in pp04),
                 "unplanned_is_a_terminal_negative":False,
                 "independent_crosswalk_between_pan_iaen":False},
    }


def query_registry(path:Path, *, cut:str="late",valid_at:str="2026-09-15",
                   family:str="all",published_until:str="as_of") -> dict:
    """Fixed enum query, all byte-level validation before any JSON projection."""
    if (type(cut) is not str or cut not in lab.CUTS or
            type(valid_at) is not str or valid_at not in VALID_DAYS or
            type(family) is not str or family not in FAMILY_FILTERS or
            type(published_until) is not str or published_until not in PUBLICATION_FILTERS):
        raise ValueError("INVALID_CLOSED_SYNTHETIC_REGISTRY_QUERY")
    as_of=lab.CUTS[cut]
    ceiling=as_of if published_until=="as_of" else published_until
    if ceiling>as_of:
        raise ValueError("REGISTRY_PUBLICATION_CEILING_AFTER_AS_OF")
    seed_registry(Path(path))
    try:
        with _connect(Path(path)) as db:
            sources,facts,edges=_audit(db)
    except sqlite3.DatabaseError as exc:
        raise RegistryIntegrityError("REGISTRY_READ_SQLITE_CORRUPTION") from exc
    visible=[s for s in sources if s["public_id"] is not None and
             (family=="all" or s["family"]==family) and
             _visible(s,as_of,ceiling)]
    registry_sources=[{
        "public_id":s["public_id"],"family":s["family"],
        "revision":"fixture_v"+str(s["revision"]),
        "descriptor_recipe":"S9_PUBLIC_SYNTHETIC_DESCRIPTOR_V1",
        "sha256_public_descriptor":s["descriptor_sha256"],
        "descriptor_byte_length":len(s["descriptor_bytes"]),
        "issuer_fixture":"FICTIONAL_"+s["family"],
        "first_public_at_fixture":s["first_public_known_at"],
        "captured_at_fixture":s["captured_at"],
        "real_first_public_at":None,"real_publisher_authenticated":False,
        "coverage_temporal":s["coverage_state"],
        "quality_gate":s["quality_gate"],"provenance":s["provenance"],
        "requested_purpose":s["purpose"],
        "rights_for_public_display":False,"empirical_admitted":False,
        "immutable_revision":True,
    } for s in visible]
    snapshot=_snapshot(sources=sources,facts=facts,edges=edges,
                       as_of=as_of,valid_at=valid_at,family=family,
                       published_until=ceiling)
    # A separate, reproducible receipt for the exact PUBLIC query projection.
    # No private source bytes/IDs, no claim of an independent publisher's sig.
    receipt_scope={
        "schema":"pfl.synthetic_scientific_registry_snapshot.v1",
        "cut":cut,"as_of":as_of,"valid_at":valid_at,
        "family":family,"published_until":ceiling,
        "distributions":registry_sources,
        "snapshot":snapshot,
    }
    canonical_snapshot=_json(receipt_scope)
    snapshot_receipt={
        "schema":"pfl.synthetic_registry_snapshot_receipt.v1",
        "canonicalization":"JSON_UTF8_SORTED_KEYS_COMPACT_V1",
        "content_scope":"CLOSED_PUBLIC_SYNTHETIC_QUERY_ONLY",
        "bytes":len(canonical_snapshot.encode("utf-8")),
        "sha256":_sha(canonical_snapshot.encode("utf-8")),
        "canonical_json":canonical_snapshot,
        "external_authenticity_certified":False,
    }
    return {
        "schema":"pfl.synthetic_scientific_registry.v1",
        "evidence_class":SYNTHETIC_ONLY,
        "cut":cut,"as_of":as_of,"valid_at":valid_at,
        "family":family,"published_until":ceiling,
        "registry": {
            "schema_version":SCHEMA_VERSION,"persistent":True,
            "migration_history":[1,2],
            "source_catalog_kind":"FIXED_PUBLIC_DESCRIPTORS_ONLY",
            "distributions":registry_sources,
            "visible_distribution_count":len(registry_sources),
            "recorded_distribution_count":6,
            "internal_uncatalogued_fixture_receipts":1,
            "source_bytes_exposed":False,
            "private_source_ids_exposed":False,
            "originals_accepted":False,
            "fixture_bytes_sha256_checked_at_read":True,
        },
        "snapshot":snapshot,
        "snapshot_receipt":snapshot_receipt,
        "snapshot_receipt_sha256":snapshot_receipt["sha256"],
        "models": {
            "s3_s7_endpoint":"/api/scientific-integration-lab",
            "computed_from_registry":False,
            "separate_existing_python_node_oracle":True,
            "empirical_model_admitted":False,
        },
        "R5":"STOP_R5", "independent_denominator":None,
        "real_source_ingestion_allowed":False,"scientific_ab_cycles":0,
        "release_gates_passed":0,
    }


def main() -> None:
    """Offline allowlisted CLI: no input paths to ingest; only local DB path."""
    import argparse
    ap=argparse.ArgumentParser(description="Seed or inspect fixed synthetic S9 registry")
    ap.add_argument("--db",type=Path,required=True,
                    help="Path for *synthetic* SQLite registry; no source bytes accepted")
    ap.add_argument("--seed",action="store_true",
                    help="atomically replay the same hardcoded fictional fixture")
    args=ap.parse_args()
    seed_registry(args.db)
    if args.seed:
        print(_json({"schema":"pfl.synthetic_registry_offline_seed.v1",
                     "status":"FIXTURE_REPLAY_VERIFIED", "R5":"STOP_R5",
                     "real_source_ingested":False}))
    else:
        print(_json(query_registry(args.db)))


if __name__=="__main__":
    main()
