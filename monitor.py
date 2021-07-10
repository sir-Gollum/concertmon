# coding: utf-8

import os

from prettytable import PrettyTable, ALL
from concerts_monitor import last_fm
from concerts_monitor import bandsintown
from concerts_monitor import backstage
from concerts_monitor import data

if __name__ == '__main__':
    LASTFM_USERNAME = os.environ['LASTFM_USERNAME']
    LASTFM_API_KEY = os.environ['LASTFM_API_KEY'] 
    LASTFM_PAGES_TO_FETCH = int(os.environ.get('LASTFM_PAGES_TO_FETCH', '20'))
    EMAIL = os.environ['EMAIL']

    COUNTRIES = os.environ.get('COUNTRIES').split()
    CITIES = os.environ.get('CITIES').split()

    DEBUG_BANDS = os.environ.get('DEBUG_BANDS')

    if DEBUG_BANDS:
        bands = [data.Band(b, 123) for b in DEBUG_BANDS.split(',')]
    else:
        bands = last_fm.get_top_bands(LASTFM_PAGES_TO_FETCH, LASTFM_USERNAME, LASTFM_API_KEY)

    print(f'Got {len(bands)} bands')
    with open(os.path.join(os.path.dirname(__file__), 'bands_blacklist.txt')) as f:
        blacklist = set([l.strip() for l in f.read().split(u'\n')])

    print('Filtering blacklist...')
    whitelisted_bands = [b for b in bands if b.name not in blacklist]
    print(f'Left with {len(whitelisted_bands)} after filtering')

    # Bandsintown
    bit_events = bandsintown.check_bands(bands=whitelisted_bands, email=EMAIL)
    bit_events = [e for e in bit_events if e.is_interesting(countries=COUNTRIES, cities=CITIES)]
    bit_events.sort(key=lambda x: x.dt)

    table_keys = ["Play Count", "Bands", "Venue / Title", "Date"]
    bit_report = PrettyTable(table_keys)
    for k in table_keys:
        bit_report.align[k] = 'l'

    for e in bit_events:
        bit_report.add_row([
            e.bands.playcount,
            e.bands.name,
            e.title,
            e.dt.strftime('%a, %d.%m.%Y %H:%M'),
        ])

    # Backstage
    bs_events = backstage.sort_and_deduplicate_events(backstage.get_backstage_events())
    print(f'Got {len(bs_events)} backstage events')

    table_keys = ["Matches", "Title", "Date"]
    bs_report = PrettyTable(table_keys, hrules=ALL)
    for k in table_keys:
        bs_report.align[k] = 'l'

    for e in bs_events:
        m = e.match_favourite(whitelisted_bands)
        if not m or 'abgesagt' in e.title.lower():
            continue
        bs_report.add_row([
            '\n'.join([str(band) for band in m]) if m else '',
            # '!!!' if e.is_interesting(whitelisted_bands) else '',
            e.title.title(),
            e.dt.strftime('%a, %d.%m.%Y %H:%M')
        ])

    print("\n========== Reports ==========")
    print("Bands-in-town events:")
    print(bit_report)
    print("Backstage events:")
    print(bs_report)
