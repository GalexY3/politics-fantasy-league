-- PostgreSQL 15+. Research schema v0.1: no data loaded or schema migration verified.
-- Avoid names as primary keys; preserve source lineage and bitemporal versioning.

CREATE TABLE source_system (
  source_id TEXT PRIMARY KEY,
  agency TEXT NOT NULL,
  catalog_url TEXT NOT NULL,
  license_status TEXT NOT NULL DEFAULT 'PENDING_REVIEW',
  parser_version TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE raw_document (
  raw_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES source_system(source_id),
  url TEXT NOT NULL,
  fetched_at TIMESTAMPTZ NOT NULL,
  http_status SMALLINT NOT NULL CHECK (http_status BETWEEN 100 AND 599),
  sha256 CHAR(64) NOT NULL,
  original_path TEXT NOT NULL,
  content_type TEXT,
  etag TEXT,
  last_modified TEXT,
  byte_count BIGINT NOT NULL CHECK (byte_count >= 0),
  ingestion_version TEXT NOT NULL,
  UNIQUE(source_id, url, sha256)
);

CREATE TABLE person (
  person_id UUID PRIMARY KEY,
  canonical_name TEXT NOT NULL,
  verified_identity BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE person_source_id (
  source_id TEXT NOT NULL REFERENCES source_system(source_id),
  external_id TEXT NOT NULL,
  person_id UUID NOT NULL REFERENCES person(person_id),
  verification_method TEXT NOT NULL,
  verified_at TIMESTAMPTZ,
  PRIMARY KEY(source_id, external_id)
);

CREATE TABLE organization (
  organization_id UUID PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN ('PARTY','PARLIAMENTARY_GROUP','CHAMBER','COMMITTEE','MINISTRY','OTHER')),
  name TEXT NOT NULL
);

CREATE TABLE mandate (
  mandate_id UUID PRIMARY KEY,
  person_id UUID NOT NULL REFERENCES person(person_id),
  institution_id UUID NOT NULL REFERENCES organization(organization_id),
  role TEXT NOT NULL,
  valid_from TIMESTAMPTZ NOT NULL,
  valid_to TIMESTAMPTZ,
  group_id UUID REFERENCES organization(organization_id),
  party_id UUID REFERENCES organization(organization_id),
  known_from TIMESTAMPTZ NOT NULL,
  known_to TIMESTAMPTZ,
  provenance_raw_id BIGINT NOT NULL REFERENCES raw_document(raw_id),
  CHECK (valid_to IS NULL OR valid_to > valid_from),
  CHECK (known_to IS NULL OR known_to > known_from)
);
CREATE INDEX idx_mandate_valid_time ON mandate(person_id,valid_from,valid_to);

CREATE TABLE legislative_case (
  case_id UUID PRIMARY KEY,
  chamber_id UUID NOT NULL REFERENCES organization(organization_id),
  source_case_key TEXT NOT NULL,
  case_kind TEXT,
  title TEXT,
  UNIQUE(chamber_id,source_case_key)
);

CREATE TABLE political_event (
  event_id UUID PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES source_system(source_id),
  external_event_key TEXT NOT NULL,
  case_id UUID REFERENCES legislative_case(case_id),
  event_kind TEXT NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL,
  first_public_at TIMESTAMPTZ NOT NULL,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  payload JSONB NOT NULL,
  provenance_raw_id BIGINT NOT NULL REFERENCES raw_document(raw_id),
  source_revision TEXT NOT NULL,
  supersedes_event_id UUID REFERENCES political_event(event_id),
  UNIQUE(source_id, external_event_key, source_revision)
);
CREATE INDEX idx_event_time ON political_event(occurred_at, first_public_at);
CREATE INDEX idx_event_kind ON political_event(event_kind);

CREATE TABLE event_participation (
  event_id UUID NOT NULL REFERENCES political_event(event_id),
  person_id UUID NOT NULL REFERENCES person(person_id),
  involvement TEXT NOT NULL CHECK (involvement IN ('VOTER','SPEAKER','PROPONENT','SIGNATORY','OFFICE_HOLDER','OTHER')),
  source_statement TEXT,
  provenance_raw_id BIGINT NOT NULL REFERENCES raw_document(raw_id),
  attribution_method TEXT NOT NULL,
  verification_state TEXT NOT NULL DEFAULT 'PENDING',
  PRIMARY KEY (event_id,person_id,involvement)
);

CREATE TABLE vote_detail (
  event_id UUID NOT NULL REFERENCES political_event(event_id),
  person_id UUID NOT NULL REFERENCES person(person_id),
  vote TEXT NOT NULL CHECK (vote IN ('YES','NO','ABSTAIN','ABSENT','NOT_RECORDED','OTHER')),
  PRIMARY KEY(event_id, person_id)
);

-- Fantasy club is NOT a real political party.
CREATE TABLE fantasy_club (
  club_id UUID PRIMARY KEY,
  display_name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE fantasy_round (
  round_id UUID PRIMARY KEY,
  starts_at TIMESTAMPTZ NOT NULL,
  ends_at TIMESTAMPTZ NOT NULL,
  lineup_lock_at TIMESTAMPTZ NOT NULL,
  scoring_version TEXT NOT NULL,
  CHECK (ends_at > starts_at),
  CHECK (lineup_lock_at <= starts_at)
);
CREATE TABLE fantasy_lineup (
  club_id UUID NOT NULL REFERENCES fantasy_club(club_id),
  round_id UUID NOT NULL REFERENCES fantasy_round(round_id),
  person_id UUID NOT NULL REFERENCES person(person_id),
  position TEXT NOT NULL,
  locked_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY(club_id,round_id,person_id)
);
CREATE TABLE fantasy_scoring_event (
  round_id UUID NOT NULL REFERENCES fantasy_round(round_id),
  event_id UUID NOT NULL REFERENCES political_event(event_id),
  person_id UUID NOT NULL REFERENCES person(person_id),
  version TEXT NOT NULL,
  points NUMERIC(12,4) NOT NULL,
  adjudication TEXT NOT NULL,
  PRIMARY KEY(round_id,event_id,person_id,version)
);

-- Prediction provenance; no mixing prediction and ground-truth state.
CREATE TABLE model_run (
  run_id UUID PRIMARY KEY,
  model_name TEXT NOT NULL,
  code_commit_sha TEXT,
  training_cutoff TIMESTAMPTZ NOT NULL,
  prediction_as_of TIMESTAMPTZ NOT NULL,
  prediction_target TEXT NOT NULL,
  feature_manifest_sha256 CHAR(64) NOT NULL,
  holdout_state TEXT NOT NULL,
  metrics JSONB
);

-- Bitemporal information rule for analytics:
-- Query any row only if first_public_at <= :as_of AND recorded_at <= :as_of;
-- if stored later, reconstruct historic public availability separately from ingestion availability.
-- Effective event/cargo time must never be substituted for knowledge time.