"""Synthetic tampering and agreement oracle for PAN two-engine metadata QA."""
import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pan2024_crossengine_audit.py"
spec = importlib.util.spec_from_file_location("pan2024_crossengine_audit", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def fixture():
    return ({
        "source_local_ordinal_not_official_id": 1,
        "normative_class": "LAW",
        "title_pdf_page": 45, "objective_pdf_page": 45, "ministry_pdf_page": 46,
        "title_first_line_unverified": "LEY ORGÁNICA DE EJEMPLO",
        "first_ministry_line_unverified": "Ministerio de Administración Ficticia",
    },)


def test_accent_and_case_variants_do_not_create_fake_differences():
    a = fixture()
    b = ({**a[0], "title_first_line_unverified": "ley organica de ejemplo",
          "first_ministry_line_unverified": "MINISTERIO DE ADMINISTRACION FICTICIA"},)
    audit = mod.compare_rows(a, b)
    assert audit["all_rows_agree_on_six_fields"] is True
    assert audit["row_count"] == 1
    assert audit["source_independent_denominator"] is False


@pytest.mark.parametrize("key,value", [
    ("title_pdf_page", 47), ("objective_pdf_page", 47),
    ("ministry_pdf_page", 47), ("normative_class", "ROYAL_DECREE"),
    ("title_first_line_unverified", "LEY EXTRAÑA Y DISTINTA"),
    ("first_ministry_line_unverified", "MINISTERIO FICTICIO DIFERENTE"),
])
def test_each_of_six_fields_must_detect_a_mutation(key, value):
    a = fixture()
    b = ({**a[0], key: value},)
    audit = mod.compare_rows(a, b)
    assert audit["all_rows_agree_on_six_fields"] is False
    assert audit["disagreements_by_field"][key] == 1
    assert audit["disagreement_ordinals_private"][key] == [1]


def test_wrong_length_and_same_ordinal_replay_rejected():
    a = fixture()
    with pytest.raises(mod.cohort.CohortGateError, match="INCOMPATIBLE_ROW_GRAIN"):
        mod.compare_rows(a, ())
    with pytest.raises(mod.cohort.CohortGateError, match="ORDINAL_GRAIN_DRIFT"):
        mod.compare_rows(a, ({**a[0], "source_local_ordinal_not_official_id": 2},))


def test_only_source_hash_pinned_original_accepted(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    p = outside / "PAN_2024.pdf"
    p.write_bytes(b"%PDF-1.7\nFAKE")
    with pytest.raises(mod.cohort.CohortGateError, match="SOURCE_CHANGED"):
        mod.run(pdf=p, out_dir=outside, repo_root=root)
