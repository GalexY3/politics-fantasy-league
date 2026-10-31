"""R7 regression against the *already published SIAP receipt*, no new source GET.

This is engineering evidence for clock separation, never an AB-H test:
the true first publication timestamp of the source is not known.
"""
import json
from pathlib import Path

from politics_fantasy.documentary_availability_intervals import RevisionWitness

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data/source_manifests/catalunya_siap_page1_20261031.json'
EXPECTED_META_SHA='3846b9fec8f20b426bfa1c231b717e0c20664d08aaf8586e49171339d927fc8d'


def test_real_source_receipt_cannot_become_historical_source_availability():
    manifest=json.loads(MANIFEST.read_text(encoding='utf8'))
    assert manifest['original_sha256']==EXPECTED_META_SHA
    assert manifest['source_local_process_links_unique_page_one']==20
    assert manifest['index_pages_captured']==1
    assert manifest['index_pages_advertised']==44
    assert manifest['historical_first_public_at'] is None
    w=RevisionWitness(
        revision_id='SIAP_INDEX_PAGE1_20261031',
        original_sha256=manifest['original_sha256'],
        captured_at=manifest['capture_completed_utc'],
        captured_clock_precision='SECOND',
        positive_basis='LOCAL_VERIFIED_CAPTURE',
        source_evidence_class='REAL_LOCAL_CAPTURE_ONLY',
    )
    before=w.temporal_report(as_of='2026-10-31T06:02:48.999999Z',
                            purpose='LOCAL_OBSERVATORY')
    assert before['status']=='NOT_ADMITTED_AT_CUT'
    known=w.temporal_report(as_of='2026-10-31T06:02:49Z',
                           purpose='LOCAL_OBSERVATORY')
    assert known['status']=='LOCAL_OBSERVATION_ONLY'
    assert known['first_public_at'] is None
    assert known['public_revision_usable'] is False
    past=w.temporal_report(as_of='2023-01-01T00:00:00Z',
                          purpose='HISTORICAL_PUBLIC_PREDICTOR')
    later=w.temporal_report(as_of='2026-11-01T00:00:00Z',
                           purpose='HISTORICAL_PUBLIC_PREDICTOR')
    assert past['revision_id'] is None
    assert later['revision_id'] is None
    assert not later['public_revision_usable']
