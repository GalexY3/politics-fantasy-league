"""Exploratory, aggregate-only name candidate coverage; NEVER identity adjudication."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys
import unicodedata
import xml.etree.ElementTree as ET

EXPECTED = (
    "f5753278d0b6dab8fc43f88f69ec2de35ffc1d0fbb48ddff1e407c877a6b9063",
    "671436ba27f90aa9c19fc342fc8508f7d1ddf122aa422b64edca5d6b150a6a71",
)


def normalize(value):
    decomposed = unicodedata.normalize("NFKD", value or "").casefold()
    plain = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join("".join(c if c.isalnum() else " " for c in plain).split())


def read(path, expected):
    blob = Path(path).read_bytes()
    if hashlib.sha256(blob).hexdigest() != expected:
        raise ValueError("Input hash differs from RC03 snapshot; use a new audit")
    return ET.fromstring(blob)


def candidate_counts(senators, names):
    index = defaultdict(set)
    for i, person in enumerate(senators):
        name, surname = person.findtext("nombre") or "", person.findtext("apellidos") or ""
        for label in (normalize(name + " " + surname), normalize(surname + " " + name)):
            if label:
                index[label].add(i)
    unique_labels = Counter()
    vote_rows = Counter()
    for name, rows in names.items():
        count = len(index.get(name, set()))
        category = "zero" if count == 0 else "one" if count == 1 else "multiple"
        unique_labels[category] += 1
        vote_rows[category] += rows
    return {"distinct_name_strings": {k: unique_labels[k] for k in ("zero", "one", "multiple")},
            "vote_rows": {k: vote_rows[k] for k in ("zero", "one", "multiple")}}


def main(composition, session, output):
    comp, data = read(composition, EXPECTED[0]), read(session, EXPECTED[1])
    senators = list(comp.iter("senador"))
    rows = list(data.iter("VotoSenador"))
    if not senators or not rows:
        raise ValueError("Unexpected structure or no data")
    missing = sum(not normalize(row.findtext("nombre")) for row in rows)
    names = Counter(normalize(row.findtext("nombre")) for row in rows if normalize(row.findtext("nombre")))
    # Recognize explicit XV / 15 only. Other labels remain unassigned, never guessed.
    xv = [row for row in senators if normalize(row.findtext("legislatura")) in {"xv", "15", "xv legislatura", "legislatura xv"}]
    result = {"id": "RC04-20261027", "source_sha256": list(EXPECTED),
        "method": "casefold + accent/punctuation/space normalization; exact equality to first-last or last-first labels",
        "vote_rows_total": len(rows), "empty_name_rows": missing,
        "distinct_nonempty_normalized_name_strings": len(names),
        "composition_rows_all": len(senators), "composition_rows_xv_recognized": len(xv),
        "legislature_values": dict(sorted(Counter((row.findtext("legislatura") or "").strip() for row in senators).items())),
        "all_legislatures": candidate_counts(senators, names),
        "xv_only": candidate_counts(xv, names) if xv else None,
        "xv_recognition": "EXACT_LABELS_ONLY" if xv else "NOT_ESTIMABLE",
        "identity_verified": False, "first_publication_verified": False,
        "limits": "Candidate name matches only. Snapshot may not describe the session's composition; no independent identity labels or validation."}
    assert sum(result["all_legislatures"]["distinct_name_strings"].values()) == len(names)
    assert sum(result["all_legislatures"]["vote_rows"].values()) == len(rows) - missing
    if result["xv_only"]:
        assert sum(result["xv_only"]["distinct_name_strings"].values()) == len(names)
        assert sum(result["xv_only"]["vote_rows"].values()) == len(rows) - missing
    Path(output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: python audit_senado_name_candidates_20261027.py COMPOSITION.xml SESSION.xml OUTPUT.json")
    main(*sys.argv[1:])
