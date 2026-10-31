"""PP04 cross-parser noncycle QA: synthetic fixtures, never original PDF text."""
from pathlib import Path
import importlib.util

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pp04_iaen_crossparser_private.py"
spec = importlib.util.spec_from_file_location("pp04_iaen_crossparser_private", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def fake():
    old = [{
        "source_local_ordinal": 1,
        "source_pdf_page": 40,
        "source_ministry_section": 2,
        "source_listing_heading": "APPROVED_AS_REPORTED",
        "title_candidate": "Ley de Estrella inventada. Observaciones sin relevancia",
        "first_public_at": None,
        "publisher_stable_id_verified": False,
        "policy_outcome_causally_attributed": False,
    }]
    new = [{
        "population": "PLANNED",
        "pdf_page": 40,
        "department_number": "2",
        "status_in_report": "APPROVED_AS_OF_REPORT",
        "bullet_line_text": "- Ley de Estrella inventada.",
        "first_public_at": None,
        "authenticated_pan_item_link": None,
    }]
    return old, new


def test_equal_source_local_anchors_but_extended_label_requires_review():
    a, b = fake()
    out = module.compare(a, b, n=1)
    assert out["structural_comparisons"]["ordinal_matches"] == 1
    assert out["structural_comparisons"]["page_matches"] == 1
    assert out["structural_comparisons"]["section_matches"] == 1
    assert out["structural_comparisons"]["status_matches"] == 1
    assert out["structural_comparisons"]["title_initial_four_tokens_matches"] == 1
    assert out["authenticated_pan_iaen_links"] == 0


def test_starting_token_drift_does_not_pass_by_equal_counts():
    a, b = fake()
    b[0]["bullet_line_text"] = "- Decreto de otra cosa inventada"
    result = module.compare(a, b, n=1)
    assert result["structural_comparisons"]["title_initial_four_tokens_disagrees"] == 1
    assert result["review_locations_without_original_text"][0]["ordinal"] == 1


def test_wrong_planned_unplanned_or_historical_claim_stops():
    a, b = fake()
    b[0]["population"] = "UNPLANNED"
    with pytest.raises(module.ParityError, match="NONPLANNED"):
        module.compare(a, b, n=1)
    b[0]["population"] = "PLANNED"
    b[0]["authenticated_pan_item_link"] = "SYN:FAKE"
    with pytest.raises(module.ParityError, match="REAL_CAUSAL"):
        module.compare(a, b, n=1)


def test_missing_item_and_git_output_rejected(tmp_path):
    with pytest.raises(module.ParityError, match="CENSUS_INVALID"):
        module.compare([], [], n=1)
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    out = repo / "private"
    out.mkdir()
    with pytest.raises(module.ParityError, match="OUTSIDE_GIT"):
        module.offgit(out)


def test_original_source_sha_cannot_change_silently(tmp_path):
    f = tmp_path / module.P11_NAME
    f.write_bytes(b"not a real IAEN derivative")
    with pytest.raises(module.ParityError, match="SHA256_MISMATCH"):
        module.read_pinned(f, module.P11_NAME, module.P11_SHA)
