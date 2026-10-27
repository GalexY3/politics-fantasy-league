"""Fictional negative controls for the exploratory Senate name join."""
from collections import Counter
import importlib.util
from pathlib import Path
from xml.etree.ElementTree import fromstring

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/audit_senado_name_candidates_20261027.py"
spec = importlib.util.spec_from_file_location("senado_candidates", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_ambiguous_missing_and_unique_names_are_kept_separate():
    rows = [
        fromstring("<senador><nombre>Álex</nombre><apellidos>Sol</apellidos></senador>"),
        fromstring("<senador><nombre>Eva</nombre><apellidos>Luz</apellidos></senador>"),
        fromstring("<senador><nombre>Eva</nombre><apellidos>Luz</apellidos></senador>"),
    ]
    labels = Counter({module.normalize("Sol, Alex"): 3,
                      module.normalize("Eva Luz"): 2,
                      module.normalize("Sin Par"): 1})
    result = module.candidate_counts(rows, labels)
    assert result["distinct_name_strings"] == {"zero": 1, "one": 1, "multiple": 1}
    assert result["vote_rows"] == {"zero": 1, "one": 3, "multiple": 2}
