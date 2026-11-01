"""Only synthetic text fixtures; no official PDF is needed to run these tests."""
from pathlib import Path

import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.pan_iaen_original_frame import (
    parse_plan_candidate_blocks, parse_report_ministry_listings,
    reconcile_counts_without_crosswalk, require_private_output_directory,
    verify_exact_original_sha256, rank_counts,
)


PAN = ("9. PLAN ANUAL NORMATIVO\nI. SECCION\n1. Reales Decretos\n"
       "REAL DECRETO ALFA\nObjetivo: objeto alfa\nMinisterio: A\n"
       "Coproponentes: B\nLEY BETA\nObjetivo: objeto beta\nMinisterio: B\n")
IAEN = ("4. SEGUIMIENTO POR MINISTERIOS\n"
        "4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN ANUAL\n"
        "NORMATIVO 2024\nI. Aprobadas\n"
        "- Real Decreto alfa.\nPublicado como: Real Decreto 10/2024.\n"
        "II. Pendientes de aprobación\n- Ley beta.\n"
        "4.1.2.- NORMAS APROBADAS NO INCLUIDAS EN EL PLAN ANUAL\n"
        "NORMATIVO 2024\n- Real Decreto externo.\n"
        "4.22.1.- NORMAS APRO BADAS NO INCLUIDAS E N EL PLAN ANUAL\n"
        "NORMATIVO 2024\n- Real Decreto aún más externo.\n"
        "5. REALES DECRETOS-LEYES\nReal Decreto-ley 1/2024.\n")


def test_pan_markers_are_bounded_source_local_candidates_not_confirmed_ids():
    rows = parse_plan_candidate_blocks((PAN,), expected_count=2)
    assert len(rows) == 2
    assert [x["source_local_ordinal"] for x in rows] == [1, 2]
    assert rows[0]["source_pdf_page"] == 1
    assert rows[0]["title_candidate"].startswith("REAL DECRETO ALFA")
    assert rows[1]["title_candidate"].startswith("LEY BETA")
    assert all(x["identity_authentication"] is False for x in rows)
    assert all(x["outcome"] is None for x in rows)
    assert rank_counts(rows) == {"LEY": 1, "REAL_DECRETO": 1}


def test_iaen_included_only_and_preserves_coarse_approval_status():
    result = parse_report_ministry_listings((IAEN,), expected_total=2,
                                            expected_approved=1)
    assert result["planned_listing_count"] == 2
    assert result["approved_listing_count"] == 1
    assert result["pending_approval_listing_count"] == 1
    assert result["not_included_ministry_sections"] == 1
    assert result["status_granularity"] == "APPROVED_VS_PENDING_APPROVAL_ONLY"
    assert all("externo" not in x["title_candidate"] for x in result["rows"])
    assert all(x["policy_outcome_causally_attributed"] is False for x in result["rows"])
    assert rank_counts(result["rows"], approved_only=True) == {"REAL_DECRETO": 1}


def test_section_4221_named_no_incluidas_must_not_be_promoted_to_planned():
    source = ("4.22.1.- NORMAS APRO BADAS NO INCLUIDAS E N EL PLAN ANUAL\n"
              "NORMATIVO 2024\n- Real Decreto solo externo.\n5. REALES DECRETOS-LEYES\n")
    result = parse_report_ministry_listings((source,), expected_total=0,
                                            expected_approved=0)
    assert result["planned_listing_count"] == 0
    assert result["not_included_ministry_sections"] == 1


def test_total_mismatch_never_returns_authoritative_census():
    with pytest.raises(GateError, match="PAN_MARKER_DENOMINATOR_MISMATCH"):
        parse_plan_candidate_blocks((PAN,), expected_count=198)
    with pytest.raises(GateError, match="IAEN_LISTING_DENOMINATOR_MISMATCH"):
        parse_report_ministry_listings((IAEN,), expected_total=198,
                                       expected_approved=89)


def test_no_crosswalk_even_when_global_totals_exactly_agree():
    pan = parse_plan_candidate_blocks((PAN,), expected_count=2)
    iaen = parse_report_ministry_listings((IAEN,), expected_total=2,
                                          expected_approved=1)
    report = reconcile_counts_without_crosswalk(pan, iaen)
    assert report["plan_candidate_count"] == 2
    assert report["report_planned_listing_count"] == 2
    assert report["item_crosswalk_verified"] is False
    assert report["item_level_success_rate_admissible"] is False
    assert report["as_of_first_public_at"] is None
    assert report["join_cardinality"] == "UNKNOWN"


def test_sha256_and_output_location_fail_closed(tmp_path):
    f = tmp_path / "one.pdf"
    f.write_bytes(b"%PDF-TEST-SYNTHETIC")
    with pytest.raises(GateError, match="SOURCE_ASSET_SHA256_MISMATCH"):
        verify_exact_original_sha256(f, "0" * 64)
    repo = tmp_path / "repo"
    repo.mkdir()
    with pytest.raises(GateError, match="PRIVATE_OUTPUT_MUST_BE_OUTSIDE_REPO"):
        require_private_output_directory(repo / "research" / "raw", repo)
    assert require_private_output_directory(tmp_path / "private", repo).name == "private"


def test_report_missing_category_is_not_silently_treated_as_pending():
    invalid = "4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN ANUAL\nNORMATIVO 2024\n- Ley sin clasificación.\n4.1.2.- OTRAS\n"
    with pytest.raises(GateError, match="IAEN_UNCLASSIFIED_PLANNED_LISTING"):
        parse_report_ministry_listings((invalid,), expected_total=1,
                                       expected_approved=0)


def test_publication_in_2025_does_not_retroactively_supply_2024_first_public():
    source = ("4.1.1.- INICIATIVAS NORMATIVAS INCLUIDAS EN EL PLAN ANUAL\n"
              "NORMATIVO 2024\nI. Aprobadas\n"
              "- Real Decreto previsto originalmente en 2024.\n"
              "Publicado como: Real Decreto 3/2025, de 1 de abril.\n"
              "4.1.2.- NORMAS NO INCLUIDAS\n")
    result = parse_report_ministry_listings((source,), expected_total=1,
                                            expected_approved=1)
    assert result["rows"][0]["source_listing_heading"] == "APPROVED_AS_REPORTED"
    assert result["rows"][0]["first_public_at"] is None
    assert "2025" in result["rows"][0]["source_block_private"]


def test_source_page_numbers_include_original_pdf_offset():
    first, second = PAN.split("Coproponentes: B\n", 1)
    text = "Coproponentes: B\n".join((first, second))
    rows = parse_plan_candidate_blocks((text,), expected_count=2,
                                       first_pdf_page=37)
    assert [x["source_pdf_page"] for x in rows] == [37, 37]


def test_duplicate_titles_do_not_collapse_distinct_source_local_occurrences():
    duplicated = ("9. PLAN ANUAL NORMATIVO\nREAL DECRETO ALFA\n"
                  "Objetivo: objetivo 1\nMinisterio: A\n"
                  "REAL DECRETO ALFA\nObjetivo: objetivo 2\nMinisterio: A\n")
    rows = parse_plan_candidate_blocks((duplicated,), expected_count=2)
    assert len(rows) == 2
    assert rows[0]["source_local_ordinal"] != rows[1]["source_local_ordinal"]
    assert rows[0]["publisher_stable_id_verified"] is False


def test_unrecognized_report_section_label_fails_closed():
    unknown = "4.1.1.- INICIATIVAS NORMATIVAS DE CLASE DESCONOCIDA\n- Real Decreto alfa.\n"
    with pytest.raises(GateError, match="IAEN_UNRECOGNIZED_MINISTRY_SECTION_ROLE"):
        parse_report_ministry_listings((unknown,), expected_total=1,
                                       expected_approved=0)
