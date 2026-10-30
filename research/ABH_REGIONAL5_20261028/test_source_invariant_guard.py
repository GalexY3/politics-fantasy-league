import unittest
from source_invariant_guard import audit_electoral_scope

def galicia():
    row = lambda name, seats, v: {'id': name, 'seats': seats,
        'counts': dict(zip(('registered','voters','candidacy','blank','valid','null'), v))}
    p = [row('A Coruña',25,[1088529,619409,608185,5938,614123,5286]),
         row('Lugo',14,[337745,189939,186070,1663,187733,2206]),
         row('Ourense',14,[355833,178353,176022,1105,177127,1226]),
         row('Pontevedra',22,[911709,528243,518428,4346,522774,5469])]
    return {'election_kind':'GALICIA_PARL_2024','seat_scope':'province','seats':75,
            'totals':dict(zip(('registered','voters','candidacy','blank','valid','null'),
                          [2693816,1515944,1488705,13052,1501757,14187])), 'districts':p}

def europe():
    return {'election_kind':'SPAIN_EU_2024','seat_scope':'state','seats':61,
            'totals':dict(zip(('registered','voters','candidacy','blank','valid','null'),
                    [38050286,17652007,17402783,124655,17527438,124569]))}

class SourceIntegrity(unittest.TestCase):
    def test_reconciled_galicia_pass(self):
        self.assertEqual(audit_electoral_scope(galicia())['status'], 'COHERENT_TRANSCRIPTION_NOT_AUTHENTICATED')
    def test_europe_national_pass(self):
        self.assertEqual(audit_electoral_scope(europe())['seat_scope'],'state')
    def test_dog_original_plus_100_fails(self):
        x=galicia();x['totals']['candidacy']+=100;x['totals']['valid']+=100
        with self.assertRaisesRegex(ValueError,'BALLOT_IDENTITY_FAIL|PROVINCE_SUM_MISMATCH'):
            audit_electoral_scope(x)
    def test_tampered_province_nulls_fail(self):
        x=galicia();x['districts'][0]['counts']['null']+=1
        with self.assertRaisesRegex(ValueError,'BALLOT_IDENTITY_FAIL'):audit_electoral_scope(x)
    def test_double_district_fails(self):
        x=galicia();x['districts'][1]['id']='A Coruña'
        with self.assertRaisesRegex(ValueError,'DUPLICATE_OR_INVALID_DISTRICT'):audit_electoral_scope(x)
    def test_treat_europe_as_province_seats_fails(self):
        x=europe();x['seat_scope']='province'
        with self.assertRaisesRegex(ValueError,'INVALID_SEAT_SCOPE'):audit_electoral_scope(x)
    def test_attach_euro_province_seat_rows_fails(self):
        x=europe();x['districts']=[{'id':'Madrid','seats':1}]
        with self.assertRaisesRegex(ValueError,'PROVINCE_SEAT_ALLOCATION_FORBIDDEN'):audit_electoral_scope(x)
    def test_invalid_integer_type_fails(self):
        x=europe();x['totals']['null']=True
        with self.assertRaisesRegex(ValueError,'INVALID_COUNT_null'):audit_electoral_scope(x)
    def test_empty_provinces_fails(self):
        x=galicia();x['districts']=[]
        with self.assertRaisesRegex(ValueError,'INCOMPLETE_DISTRICTS'):audit_electoral_scope(x)

if __name__ == '__main__': unittest.main()
