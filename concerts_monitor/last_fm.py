# coding: utf-8
from operator import attrgetter
from requests_futures.sessions import FuturesSession
from .data import Band


def get_top_bands(pages_to_fetch, lastfm_username, lastfm_api_key):
    result = []
    futures = []
    future_session = FuturesSession(max_workers=10)

    for page_idx in range(pages_to_fetch):
        url = 'http://ws.audioscrobbler.com/2.0/'
        params = {
            'method': 'user.gettopartists',
            'user': lastfm_username,
            'api_key': lastfm_api_key,
            'format': 'json',
            'period': 'overall',
            'page': page_idx+1,
        }
        futures.append((future_session.get(url, params=params), page_idx))

    for future, page_idx in futures:
        j = future.result().json()
        artists = j.get('topartists', {}).get('artist', [])
        for a in artists:
            name = a.get('name', None)
            pc = int(a.get('playcount', 0))
            if name and pc:
                result.append(Band(name=name, playcount=pc))

    return sorted(result, key=attrgetter('playcount'), reverse=True)
