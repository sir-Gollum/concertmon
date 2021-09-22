# coding: utf-8

import os
import tabulate
from concerts_monitor import last_fm
from concerts_monitor import bandsintown
from concerts_monitor import backstage


def get_env_bool(name, default):
    v = os.environ.get(name)
    if v is None:
        return default
    return v.lower() in {'true', 't', 'yes'}


if __name__ == '__main__':
    LASTFM_USERNAME = os.environ['LASTFM_USERNAME']
    LASTFM_API_KEY = os.environ['LASTFM_API_KEY']
    LASTFM_PAGES_TO_FETCH = int(os.environ.get('LASTFM_PAGES_TO_FETCH', '20'))

    COUNTRIES = os.environ.get('COUNTRIES').split()
    CITIES = os.environ.get('CITIES').split()

    USE_BANDSINTOWN = get_env_bool('USE_BANDSINTOWN', True)
    USE_BACKSTAGE = get_env_bool('USE_BACKSTAGE', True)

    bands = last_fm.get_top_bands(LASTFM_PAGES_TO_FETCH, LASTFM_USERNAME, LASTFM_API_KEY)
    if os.environ.get('DEBUG_BANDS'):
        bands = [b for b in bands if b.name.lower() in os.environ['DEBUG_BANDS'].lower().split(',')]

    print(f'Got {len(bands)} bands')
    with open(os.path.join(os.path.dirname(__file__), 'bands_blacklist.txt')) as f:
        blacklist = set([l.strip() for l in f.read().split(u'\n')])

    print('Filtering blacklist...')
    whitelisted_bands = [b for b in bands if b.name not in blacklist]
    print(f'Left with {len(whitelisted_bands)} after filtering')

    # Bandsintown
    bit_report = []
    if USE_BANDSINTOWN:
        email = os.environ['BANDSINTOWN_EMAIL']
        bit_events = bandsintown.check_bands(bands=whitelisted_bands, email=email)
        bit_events = [e for e in bit_events if e.is_interesting(countries=COUNTRIES, cities=CITIES)]
        bit_events.sort(key=lambda x: x.dt)

        for e in bit_events:
            bit_report.append({
                'Play Count': e.bands.playcount,
                'Bands': e.bands.name,
                "Venue / Title": e.title,
                "Date": e.dt.strftime('%a, %d.%m.%Y %H:%M'),
            })

    # Backstage
    bs_report = []
    if USE_BACKSTAGE:
        bs_events = backstage.sort_and_deduplicate_events(backstage.get_backstage_events())
        print(f'Got {len(bs_events)} backstage events')

        for e in bs_events:
            m = e.match_favourite(whitelisted_bands)
            if not m or 'abgesagt' in e.title.lower():
                continue

            bs_report.append({
                "Matches": '\n'.join([str(band) for band in m]) if m else '',
                "Title": e.title.title(),
                "Date": e.dt.strftime('%a, %d.%m.%Y %H:%M'),
            })

    print("\n========== Reports ==========")
    if USE_BANDSINTOWN:
        # bandsintown report is single-line, I prefer github markdown for that
        print('Bandsintown events:')
        output_format = os.environ.get('OUTPUT_FORMAT_BANDSINTOWN', 'github')
        print(tabulate.tabulate(bit_report, headers='keys', tablefmt=output_format))
        print()

    if USE_BACKSTAGE:
        # bandsintown report is multi-line, grid is less confusing in that case
        print("Backstage events:")
        output_format = os.environ.get('OUTPUT_FORMAT_BACKSTAGE', 'grid')
        print(tabulate.tabulate(bs_report, headers='keys', tablefmt=output_format))
        print()
