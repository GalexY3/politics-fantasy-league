from politics_fantasy.majority_sign import compare_ballot, compute
import json
import pytest

def row(o_yes,o_no,n_yes,n_no):
    return {'id':'s1-v001','fecha':'2023-09-19',
        'totales':{'si':o_yes,'no':o_no,'abstencion':0,'noVota':0},
        'votos':{'S':' '.join(str(i) for i in range(n_yes)),
                 'N':' '.join(str(i) for i in range(n_no))}}

def test_strict_direction_change():
    assert compare_ballot(row(176,169,134,153))=='STRICT_REVERSAL'

def test_just_tie_change():
    assert compare_ballot(row(176,169,10,10))=='TIE_INVOLVED'

def test_same_sign():
    assert compare_ballot(row(176,169,160,150))=='SAME_SIGN'

def test_no_nominal_not_absent():
    assert compare_ballot(row(176,169,0,0))=='NO_NOMINAL'

def test_run_on_fixture(tmp_path):
    p=tmp_path/'data.jsonl';p.write_text(json.dumps(row(176,169,134,153))+'\n')
    assert compute(p,verify_blob=False)['count_by_type']['STRICT_REVERSAL']==1
    with pytest.raises(ValueError,match='Not the audited'):compute(p,verify_blob=True)
