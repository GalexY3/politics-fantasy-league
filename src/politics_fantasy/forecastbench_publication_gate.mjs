/**
 * Source-availability gate for exactly the four original PUBLIC ForecastBench
 * files pinned in PUBLIC_DATASET_PIN. Its Git commit contains the required
 * question and resolution blobs. Publication of the SOURCE FILE, not the
 * event's resolution_date, controls retrospective data eligibility.
 *
 * Dataset: Forecasting Research Institute / Karger et al (ICLR 2025),
 * forecastingresearch/forecastbench-datasets, CC BY-SA 4.0.
 * No event/participant first_public_at, no rights or publisher attestation.
 */
export const PINNED_SOURCE_PUBLICATION = Object.freeze({
  commit: '027ba0b3017a60e0e64602d724284ac6b2d91134',
  committed_at: '2026-10-29T07:30:17Z',
  first_sep27_resolution_commit: '4eafa5cdda4d9fbf3542ea9f5f71050b9dd89110',
  first_sep27_resolution_committed_at: '2026-10-07T07:19:29Z',
  scope: 'PUBLIC_GITHUB_DATASET_SNAPSHOT_NOT_PER_EVENT_PUBLICATION',
});

function parseCanonicalSecondUtc(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(value))
    throw Error('INVALID_AS_OF_INSTANT');
  const milliseconds = Date.parse(value);
  if (!Number.isFinite(milliseconds) || new Date(milliseconds).toISOString() !== value.replace('Z', '.000Z'))
    throw Error('INVALID_AS_OF_INSTANT');
  return milliseconds;
}

export function assertPublicDatasetPublished({as_of_instant,source_commit} = {}) {
  const cutoff = parseCanonicalSecondUtc(as_of_instant);
  if (source_commit !== PINNED_SOURCE_PUBLICATION.commit)
    throw Error('UNVERIFIED_SOURCE_COMMIT');
  const published = parseCanonicalSecondUtc(PINNED_SOURCE_PUBLICATION.committed_at);
  if (cutoff < published) throw Error('SOURCE_NOT_PUBLIC_AT_CUTOFF');
  return Object.freeze({
    declared_original_commit: PINNED_SOURCE_PUBLICATION.commit,
    git_commit_at: PINNED_SOURCE_PUBLICATION.committed_at,
    evaluated_at: as_of_instant,
    event_cutoff_date: as_of_instant.slice(0, 10),
    original_git_snapshot_available_at_cutoff: true,
    only_source_file_availability: true,
    per_record_first_public_at_verified: false,
    other_market_sources_checked: false,
    personal_forecasts_processed: false,
    rights_independently_attested: false,
    release_ready: false,
  });
}
