/**
 * PFL ABH30-C09 — Public non-person source raw-record revision guard.
 * Input objects are already-parsed public source snapshots (NOT source authenticators).
 * This pure component does not read network/files, retain person data or print source IDs.
 * Git blob authentication and source-as-of selection remain upstream obligations.
 */
const UTC = /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/;
function millis(s) {
  if (typeof s !== 'string' || !UTC.test(s)) throw Error('INVALID_UTC_SECONDS');
  const t = Date.parse(s);
  if (!Number.isFinite(t) || new Date(t).toISOString() !== s.replace('Z', '.000Z'))
    throw Error('INVALID_UTC_SECONDS');
  return t;
}
function normalized(value) {
  if (Array.isArray(value)) return value.map(normalized);
  if (value && typeof value === 'object') {
    const o = {};
    for (const key of Object.keys(value).sort()) {
      if (key === '__proto__' || key === 'constructor' || key === 'prototype')
        throw Error('UNSAFE_PUBLIC_RECORD_FIELD');
      o[key] = normalized(value[key]);
    }
    return o;
  }
  if (typeof value === 'number' && !Number.isFinite(value)) throw Error('NONFINITE_PUBLIC_RECORD');
  return value;
}
function keyed(snapshot) {
  const d = snapshot?.data;
  if (!d || !Array.isArray(d.resolutions) ||
      d.forecast_due_date !== snapshot.cohort ||
      d.question_set !== snapshot.cohort + '-llm.json')
    throw Error('PUBLIC_SOURCE_SCHEMA_MISMATCH');
  const result = new Map();
  for (const row of d.resolutions) {
    if (!row || typeof row !== 'object' || Array.isArray(row) ||
        typeof row.source !== 'string' || !row.source.trim() ||
        typeof row.id !== 'string' || !row.id.trim())
      throw Error('INVALID_PUBLIC_SOURCE_KEY');
    const key = JSON.stringify([row.source, row.id]);
    if (result.has(key)) throw Error('DUPLICATE_PUBLIC_SOURCE_KEY');
    result.set(key, JSON.stringify(normalized(row)));
  }
  return result;
}
function validated(s) {
  if (!s || typeof s !== 'object' || typeof s.cohort !== 'string' ||
      !/^\d{4}-\d\d-\d\d$/.test(s.cohort) ||
      typeof s.git_blob !== 'string' || !/^[a-f0-9]{40}$/.test(s.git_blob) ||
      typeof s.git_commit !== 'string' || !/^[a-f0-9]{40}$/.test(s.git_commit))
    throw Error('INVALID_ORIGINAL_GIT_MANIFEST');
  const time = millis(s.committed_at);
  return {s, time, records: keyed(s)};
}
export function auditPublicRawRevision(before, after) {
  const a = validated(before), b = validated(after);
  if (a.s.cohort !== b.s.cohort) throw Error('CROSS_COHORT_COMPARISON_FORBIDDEN');
  if (a.time >= b.time) throw Error('NONINCREASING_SOURCE_PUBLICATION_TIME');
  if (a.s.git_blob === b.s.git_blob)
    throw Error('NO_DISTINCT_SOURCE_BLOB');
  let removed = 0, mutated = 0, retained_unchanged = 0, added = 0;
  for (const [key, oldValue] of a.records) {
    if (!b.records.has(key)) removed++;
    else if (oldValue !== b.records.get(key)) mutated++;
    else retained_unchanged++;
  }
  for (const key of b.records.keys()) if (!a.records.has(key)) added++;
  return Object.freeze({
    schema: 'pfl.forecastbench.public_raw_revision_guard.v1',
    cohort: a.s.cohort, from_git_commit: a.s.git_commit, to_git_commit: b.s.git_commit,
    from_git_blob: a.s.git_blob, to_git_blob: b.s.git_blob,
    from_committed_at: a.s.committed_at, to_committed_at: b.s.committed_at,
    before_rows: a.records.size, after_rows: b.records.size,
    retained_unchanged, added, removed, mutated,
    count_identity_holds: a.records.size - removed + added === b.records.size,
    raw_append_only_consistent: removed === 0 && mutated === 0,
    manual_review_required: removed > 0 || mutated > 0,
    original_git_bytes_authenticated_here: false,
    individual_event_first_public_at_verified: false,
    source_personal_rows_processed: false,
    public_row_identifiers_in_output: false,
    science_grade: '0/3', launch_ready: false
  });
}
export function auditPublicRawChain(snapshots) {
  if (!Array.isArray(snapshots) || snapshots.length < 2) throw Error('TWO_OR_MORE_PUBLIC_VERSIONS_REQUIRED');
  const pairs = [];
  for (let i = 1; i < snapshots.length; i++) pairs.push(auditPublicRawRevision(snapshots[i-1], snapshots[i]));
  return Object.freeze({schema: 'pfl.forecastbench.public_raw_revision_chain.v1',
    cohort: pairs[0].cohort, revisions: pairs,
    total_removed: pairs.reduce((n,p)=>n+p.removed,0),
    total_mutated: pairs.reduce((n,p)=>n+p.mutated,0),
    no_raw_append_only_assumption: pairs.some(p=>!p.raw_append_only_consistent),
    source_authentication_independent_required: true,
    no_human_scoring: true, science_grade:'0/3'});
}
