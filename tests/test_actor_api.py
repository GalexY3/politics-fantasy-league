"""PF-BR20H synthetic-only Python adapter checks. No real people or parties."""
import json
from pathlib import Path

from politics_fantasy.actor_api import local_actor_universe_status


def test_actor_universe_missing(tmp_path):
    r = local_actor_universe_status(tmp_path / 'missing.json')
    assert r['status'] == 'NOT_AVAILABLE'
    assert r['real_people_scoring'] is False


def test_actor_universe_rejects_claimed_real_dataset(tmp_path):
    p = tmp_path / 'input.json'
    p.write_text(json.dumps({'dataset_class':'USER_PROVIDED_SOURCE_SNAPSHOT',
        'sources':[], 'actors':[], 'events':[]}))
    r = local_actor_universe_status(p)
    assert r['reason'] == 'NOT_SYNTHETIC_DATA'
    assert r['field_actors_verified'] == 0


def test_actor_universe_synthetic_counts_and_privacy(tmp_path):
    p = tmp_path / 'fixture.json'
    p.write_text(json.dumps({
        'dataset_class':'FIXTURE',
        'sources':[{'id':'s', 'kind':'FIXTURE', 'state':'FIXTURE'}],
        'actors':[{'name':'Inventada', 'kind':'PERSON'},
                  {'name':'Partido Ficticio', 'kind':'PARTY'},
                  {'name':'Plataforma Ficticia', 'kind':'CIVIC_PLATFORM'}],
        'events':[{'id':'ev'}]}))
    r = local_actor_universe_status(p)
    assert r['total_actors'] == 3
    assert r['actors_by_kind']['PERSON'] == 1
    assert r['documented_events_in_fixture'] == 1
    assert 'Inventada' not in json.dumps(r)
    assert 'Partido Ficticio' not in json.dumps(r)
    assert r['real_people_scoring'] is False


def test_actor_universe_disallows_nonfixture_source(tmp_path):
    p = tmp_path / 'fixture.json'
    p.write_text(json.dumps({'dataset_class':'FIXTURE',
      'sources':[{'kind':'OFFICIAL','state':'FIXTURE'}], 'actors':[], 'events':[]}))
    assert local_actor_universe_status(p)['reason'] == 'BAD_FIXTURE_SCHEMA'
