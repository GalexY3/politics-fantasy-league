"""Exercise redirect policy without network or a platform-dependent store."""
from urllib.request import Request

import pytest

from politics_fantasy.ingest import MAX_REDIRECTS, SourceScopedRedirects, _check_official_url


@pytest.mark.parametrize('url', [
    'https://evil.invalid/collect',
    'https://www.congreso.es.evil.invalid/collect',
    'https://www.senado.es/collect',
    'http://www.congreso.es/collect',
    'https://name@www.congreso.es/collect',
    'https://www.congreso.es:444/collect',
    'https://127.0.0.1/collect',
])
def test_guard_rejects_redirect_targets_before_returning_request(url):
    guard = SourceScopedRedirects('congreso')
    request = Request('https://www.congreso.es/start')
    with pytest.raises(ValueError, match='SOURCE_HOST_OR_SCHEME_MISMATCH'):
        guard.redirect_request(request, None, 302, 'Found', {}, url)
    assert guard.hops == []


def test_guard_accepts_same_host_then_enforces_hop_limit():
    guard = SourceScopedRedirects('congreso')
    request = Request('https://www.congreso.es/start')
    for number in range(MAX_REDIRECTS):
        request = guard.redirect_request(request, None, 302, 'Found', {},
                                         f'https://www.congreso.es/{number}')
    assert len(guard.hops) == MAX_REDIRECTS
    with pytest.raises(ValueError, match='TOO_MANY_REDIRECTS'):
        guard.redirect_request(request, None, 302, 'Found', {}, 'https://www.congreso.es/extra')


def test_initial_source_host_binding_is_independent_of_store():
    _check_official_url('https://www.congreso.es/document', 'congreso')
    with pytest.raises(ValueError, match='SOURCE_HOST_OR_SCHEME_MISMATCH'):
        _check_official_url('https://www.senado.es/document', 'congreso')
