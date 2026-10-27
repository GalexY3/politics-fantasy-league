"""Aggregate-only, reproducible profile of already explored Senate originals."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET


def load(path):
    raw = Path(path).read_bytes()
    return ET.fromstring(raw), {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main(composition, session, output):
    comp, comp_meta = load(composition)
    votes, votes_meta = load(session)
    senators = list(comp.iter("senador"))
    if comp.tag != "senadores1977" or votes.tag != "main" or not senators:
        raise ValueError("Unexpected XML schema; inspect source before use")
    values = lambda name: [(row.findtext(name) or "").strip() for row in senators]
    legislature, credential = values("legislatura"), values("ultCredencial")
    keys = Counter(zip(legislature, credential))
    comp_meta.update({"root": comp.tag, "senador_nodes": len(senators),
        "legislature_values": len(set(legislature)), "credential_values": len(set(credential)),
        "missing_legislature": sum(not x for x in legislature),
        "missing_credential": sum(not x for x in credential),
        "distinct_legislature_credential_pairs": len(keys),
        "duplicate_pairs": sum(n-1 for n in keys.values() if n > 1)})
    votes_meta.update({"root": votes.tag, "session_nodes": len(list(votes.iter("sesion"))),
        "votacion_nodes": len(list(votes.iter("votacion"))),
        "votos_senador_nodes": len(list(votes.iter("VotoSenador"))),
        "ausencia_nodes": len(list(votes.iter("ausencia")))})
    result = {"id": "RC03-20261027", "composition_url": "https://www.senado.es/web/ficopendataservlet?tipoFich=10",
        "session_url": "https://www.senado.es/legis15/votaciones/ses_60.xml",
        "composition": comp_meta, "session": votes_meta,
        "scope": "Counts of XML nodes; a candidate composite key is snapshot-specific and not a certified person identity or historical crosswalk.",
        "source_explored_before_preregistration": True, "as_of_and_first_publication_verified": False}
    Path(output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: python audit_senado_sources_20261027.py COMPOSITION.xml SESSION.xml OUTPUT.json")
    main(*sys.argv[1:])
