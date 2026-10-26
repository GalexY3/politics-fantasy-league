"""Parser negative controls; the live PDF is verified only in CI action on real bytes."""
import pathlib
import sys
import pytest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from verify_boe_table_pdf import reference_rows, parse_pdf_lines, verify

ROOT=pathlib.Path(__file__).resolve().parents[1]
REF=ROOT/"research/BRANCH30I_20261026/JEC_2023_TABLE_I_TRANSCRIPTION.psv"

def sample_text():
    return "\n".join(
        "  "+r["province"]+"    "+"     ".join(f"{n:,}".replace(",",".") for n in r["counts"])
        for r in reference_rows(REF)
    )

def sample_pdf(path):
    path.write_bytes(b"%PDF-1.5\n"+b"x"*500+b"%%EOF\n")

def test_pdf_parser_parses_52_independent_rows(tmp_path):
    original=tmp_path/"fake.pdf";sample_pdf(original)
    r=verify(original,REF,runner=sample_text())
    assert r["full_table_verified"] is True
    assert r["unique_provinces_matched"]==52
    assert r["reconciled_cells"]==312

def test_single_changed_numeric_cell_rejected(tmp_path):
    original=tmp_path/"fake.pdf";sample_pdf(original)
    old=sample_text()
    bad=old.replace("307.988","307.989",1)
    r=verify(original,REF,runner=bad)
    assert r["full_table_verified"] is False
    assert r["errors"][0]["province_code"]=="02"

def test_invalid_pdf_signature_fails(tmp_path):
    original=tmp_path/"bad.pdf";original.write_text("Not a PDF")
    with pytest.raises(ValueError,match="PDF_SIGNATURE_INVALID"):
        verify(original,REF,runner=sample_text())

def test_duplicate_province_does_not_fake_two_independent_matches(tmp_path):
    original=tmp_path/"fake.pdf";sample_pdf(original)
    duplicate=sample_text().splitlines()[0]
    r=verify(original,REF,runner=sample_text()+"\n"+duplicate)
    assert r["full_table_verified"] is False
    assert r["errors"][0]["type"]=="NOT_UNIQUELY_FOUND"
