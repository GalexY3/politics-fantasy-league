"""Validate original Senate nominal votes without certifying person identity or publication."""
from collections import Counter
from datetime import datetime
from xml.etree import ElementTree as ET

VOTE_TO_TOTAL = {
    "SÍ": "tot_afirmativos", "NO": "tot_negativos",
    "ABSTENCIÓN": "tot_abstenciones", "NO VOTAN": "tot_novotan",
}

def audit_original_senate_session(xml_bytes: bytes) -> dict:
    if not isinstance(xml_bytes, bytes):
        raise ValueError("XML_BYTES_REQUIRED")
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError("INVALID_XML") from exc
    session = root.find("sesion")
    if session is None:
        raise ValueError("MISSING_SESSION")
    try:
        session_day = datetime.strptime(session.findtext("fecha_sesion"), "%d/%m/%Y").date()
    except (TypeError, ValueError) as exc:
        raise ValueError("BAD_SESSION_DAY") from exc
    results = []
    seen_vote_numbers = set()
    seen_source_codes = set()
    for vote in session.findall("votacion"):
        number, code = vote.findtext("num_vot"), vote.findtext("CodVotacion")
        if (not number or not number.isascii() or not number.isdecimal()
                or int(number) < 1 or str(int(number)) != number
                or not code or not code.isascii() or not code.isdecimal()
                or int(code) < 1 or number in seen_vote_numbers or code in seen_source_codes):
            raise ValueError("DUPLICATE_OR_BAD_SENATE_VOTE_IDENTIFIER")
        seen_vote_numbers.add(number)
        seen_source_codes.add(code)
        raw_day = vote.findtext("fecha_v")
        try:
            parts = raw_day.upper().split("-")
            months = {"ENE":1,"FEB":2,"MAR":3,"ABR":4,"MAY":5,"JUN":6,
                      "JUL":7,"AGO":8,"SEP":9,"OCT":10,"NOV":11,"DIC":12}
            if len(parts) != 3 or parts[1] not in months:
                raise ValueError("UNKNOWN_SENATE_MONTH")
            vote_day = datetime(int(parts[2]), months[parts[1]], int(parts[0])).date()
        except (TypeError, ValueError) as exc:
            raise ValueError("BAD_VOTE_DAY") from exc
        counts = Counter()
        seen_source_seats = set()
        for person in vote.findall("./resultado/VotoSenador"):
            seat = person.findtext("escano")
            if not isinstance(seat,str) or not seat.isascii() or not seat.isdecimal() or not seat or int(seat)<1 or str(int(seat))!=seat or seat in seen_source_seats:
                raise ValueError("DUPLICATE_OR_BAD_SENATE_SEAT_IN_VOTE")
            seen_source_seats.add(seat)
            label = person.findtext("voto")
            if label not in VOTE_TO_TOTAL:
                raise ValueError("UNKNOWN_OFFICIAL_SENATE_LABEL")
            counts[label] += 1
        try:
            claimed = {tag: int(vote.findtext(tag)) for tag in
                       (*VOTE_TO_TOTAL.values(), "tot_presentes", "tot_ausentes")}
        except (TypeError, ValueError) as exc:
            raise ValueError("BAD_TOTAL_FIELD") from exc
        for label, tag in VOTE_TO_TOTAL.items():
            if counts[label] != claimed[tag]:
                raise ValueError("SENATE_VOTE_TOTAL_MISMATCH")
        absences = len(vote.findall("./ausentes/ausencia"))
        if claimed["tot_ausentes"] != absences or claimed["tot_presentes"] != sum(counts.values()):
            raise ValueError("SENATE_VOTE_TOTAL_MISMATCH")
        results.append((vote_day.isoformat(), sum(counts.values()), absences))
    if not results:
        raise ValueError("MISSING_VOTES")
    return {
        "session_header_day": session_day.isoformat(),
        "vote_days": sorted(set(x[0] for x in results)),
        "votes_verified": len(results),
        "nominal_rows_verified": sum(x[1] for x in results),
        "absences_verified": sum(x[2] for x in results),
        "first_public_at_verified": False,
        "historical_person_ID_certified": False,
        "real_person_scoring": False,
    }
