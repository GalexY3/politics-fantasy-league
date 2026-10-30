import copy
import unittest
from research_only_house_groups import audit_record, prevote_features


def fixture(year=2025, roll=180):
    if year == 2025:
        p={'Republican': {'yea': 212, 'nay': 2, 'not_voting': 9},
           'Democratic': {'yea': 7, 'nay': 204, 'not_voting': 4}}
        t={'yea': 219, 'nay': 206, 'present': 0, 'not_voting': 13}
        dt='2025-06-25'
    else:
        p={'Republican': {'yea': 199, 'nay': 5, 'not_voting': 13},
           'Democratic': {'yea': 205, 'nay': 0, 'not_voting': 7},
           'Independent': {'yea': 1, 'nay': 0, 'not_voting': 0}}
        t={'yea': 405, 'nay': 5, 'present': 0, 'not_voting': 20}
        dt='2026-05-20'
    return dict(house='US_HOUSE',year=year,roll=roll,date=dt,
                question='On Motion',vote_type='Recorded Vote',
                totals=t,parties=p,source_url=f'https://clerk.house.gov/Votes/{year}{roll}')


class HouseInvariantTests(unittest.TestCase):
    def reject(self, row, error):
        with self.assertRaisesRegex(ValueError, error):
            audit_record(row)

    def test_2025_valid(self):
        self.assertFalse(audit_record(fixture())['shared_group_majority'])

    def test_2026_valid_with_independent(self):
        self.assertTrue(audit_record(fixture(2026))['shared_group_majority'])

    def test_party_total_mismatch(self):
        x=fixture();x['totals']['yea']+=1
        self.reject(x, 'PARTY_TOTAL_MISMATCH')

    def test_missing_independent_2026(self):
        x=fixture(2026);x['parties'].pop('Independent')
        self.reject(x, 'PARTY_TOTAL_MISMATCH')

    def test_boolean_not_integer(self):
        x=fixture();x['totals']['not_voting']=True
        self.reject(x, 'INVALID_TOTAL_not_voting')

    def test_negative_votes(self):
        x=fixture();x['parties']['Republican']['nay']=-1
        self.reject(x, 'INVALID_PARTY_nay')

    def test_wrong_year_source(self):
        x=fixture();x['source_url']=x['source_url'].replace('2025','2026')
        self.reject(x, 'INVALID_SOURCE_KEY')

    def test_forged_url(self):
        x=fixture();x['source_url']='https://clerk.house.gov.evil.test/Votes/2025180'
        self.reject(x, 'INVALID_SOURCE_KEY')

    def test_impossible_date(self):
        x=fixture();x['date']='2025-02-31'
        self.reject(x, 'INVALID_DATE')

    def test_invalid_year(self):
        x=fixture();x['year']=True
        self.reject(x, 'INVALID_YEAR')

    def test_missing_procedure(self):
        x=fixture();x['question']=''
        self.reject(x, 'MISSING_PROCEDURE')

    def test_no_party_majority(self):
        x=fixture();x['parties']['Republican']['yea']=2;x['parties']['Republican']['nay']=2
        x['totals']['yea']=9;x['totals']['nay']=206
        self.reject(x, 'NO_GROUP_MAJORITY')

    def test_prevote_valid(self):
        x=fixture();s={k:x[k] for k in ('house','year','roll','date','question','vote_type')}
        self.assertEqual(prevote_features(s),s)

    def test_prevote_rejects_realized_totals(self):
        x=fixture();s={k:x[k] for k in ('house','year','roll','date','question','vote_type')}
        s['aye_margin']=13
        with self.assertRaisesRegex(ValueError, 'POSTVOTE_FEATURE_LEAK'):
            prevote_features(s)

    def test_prevote_rejects_realized_party_counts(self):
        x=fixture();s={k:x[k] for k in ('house','year','roll','date','question','vote_type')}
        s['parties']=x['parties']
        with self.assertRaisesRegex(ValueError, 'POSTVOTE_FEATURE_LEAK'):
            prevote_features(s)

if __name__=='__main__': unittest.main()
