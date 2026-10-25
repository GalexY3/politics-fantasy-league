"""Adversarial unit tests; fixtures derived from MANUAL sample and synthetic interventions."""
from pathlib import Path
import csv
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from ab20_c01_pilot import audit

PILOT = Path(__file__).resolve().parents[1] / 'data/pilot_official_webview/20260723_vote_totals_MANUAL.csv'


def mutate(tmp_path, change=None):
    with PILOT.open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames, rows = reader.fieldnames, list(reader)
    if change:
        change(rows)
    out = tmp_path / 'mutated.csv'
    with out.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    return out


def test_pilot_metrics():
    o = audit(PILOT)
    assert o['n_rows'] == 20 and o['sessions'] == 1
    assert o['total_min'] == 344 and o['total_max'] == 348
    assert o['votes_total_histogram'] == {'344':1,'346':1,'347':5,'348':13}
    assert o['total_median'] == 348


def test_negative_control_impossible_total(tmp_path):
    path = mutate(tmp_path, lambda rows: rows[0].update(yes='351'))
    with pytest.raises(ValueError, match='350'):
        audit(path)


def test_duplicate_position(tmp_path):
    path = mutate(tmp_path, lambda rows: rows[1].update(row_id=rows[0]['row_id']))
    with pytest.raises(ValueError, match='duplicated'):
        audit(path)


def test_negative_votes(tmp_path):
    path = mutate(tmp_path, lambda rows: rows[0].update(no='-1'))
    with pytest.raises(ValueError, match='negative'):
        audit(path)


def test_bad_url(tmp_path):
    path = mutate(tmp_path, lambda rows: rows[0].update(source_url='https://example.com'))
    with pytest.raises(ValueError, match='source'):
        audit(path)


def test_mixed_session(tmp_path):
    path = mutate(tmp_path, lambda rows: rows[0].update(session='194'))
    with pytest.raises(ValueError, match='session'):
        audit(path)


def test_empty_file(tmp_path):
    path = tmp_path/'empty.csv'
    path.write_text(','.join(('row_id','legislature','session','event_date','source_url','source_line_yes','yes','no','abstain','reading_method'))+'\n')
    with pytest.raises(ValueError, match='empty'):
        audit(path)