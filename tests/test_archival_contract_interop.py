"""C18: selected historical tools coexist without identity or scoring promotion."""
from politics_fantasy.congress_vote_dates import normalized_vote_date
from politics_fantasy.typed_refs import InstitutionalRef, same_institutional_record, scoring_enabled
from politics_fantasy.congress_members import project
import json


def test_three_source_contracts_coexist_without_person_identity_upgrade():
    row={
        "NOMBRE":"Apellido, Nombre","CIRCUNSCRIPCION":"Provincia",
        "FORMACIONELECTORAL":"SINTETICA","GRUPOPARLAMENTARIO":"Grupo X",
        "FECHAALTA":"07/08/2023","FECHACONDICIONPLENA":"17/08/2023",
        "FECHAALTAENGRUPOPARLAMENTARIO":"18/08/2023"
    }
    person=project(json.dumps([row]).encode("utf-8"))["people"][0]
    earlier=InstitutionalRef("Congreso","XIV","row",person["snapshot_row_id"])
    later=InstitutionalRef("Congreso","XV","row",person["snapshot_row_id"])
    assert normalized_vote_date("28/10/2026")=="2026-10-28"
    assert not same_institutional_record(earlier,later)
    assert person["first_public_at"] is None
    assert person["eligible_for_real_scoring"] is False
    assert not scoring_enabled(later)
