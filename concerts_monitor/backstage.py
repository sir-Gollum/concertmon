# coding: utf-8
import os
import requests
from lxml import html
import tabulate
from .last_fm import get_top_bands
from .data import BackstageEvent


def get_backstage_events():
    # We crawl this and don't know the number of pages in advance
    page = -1
    events = []

    while True:
        found_on_page = 0
        page += 1
        url = 'http://backstage.info/veranstaltungen-2/live'
        if page:
            url += '/' + str(page)

        print(f'Requesting {url}...')
        markup = requests.get(url).text
        etree = html.fromstring(markup)

        print(f'Parsing response from {url}...')
        for el in etree.xpath('//div[@class="items"]/*/*'):
            title = el.xpath('string((.//*[@title])[1]/@title)').strip()
            bands = el.xpath('string(.//h5)').strip()
            datetime = el.xpath('string((.//p)[1])').strip()

            if not datetime or not title + bands:
                continue
        
            events.append(BackstageEvent(title=title, bands=bands, dt=datetime))
            found_on_page += 1

        print(f'Found {found_on_page} events on {url}')
        if not found_on_page:
            break

    return events


def sort_and_deduplicate_events(events):
    events = sorted(events, key=lambda e: (e.dt, e.title, e.bands))
    result = []
    for e in events:
        if result and str(e) == str(result[-1]):
            continue
        result.append(e)
    return result


if __name__ == '__main__':
    LASTFM_USERNAME = os.environ['LASTFM_USERNAME']
    LASTFM_API_KEY = os.environ['LASTFM_API_KEY'] 
    LASTFM_PAGES_TO_FETCH = 5

    bands = get_top_bands(LASTFM_PAGES_TO_FETCH, LASTFM_USERNAME, LASTFM_API_KEY)
    print(f'Got {len(bands)} bands')
    events = sort_and_deduplicate_events(get_backstage_events())
    print(f'Got {len(events)} events')

    with open(os.path.join(os.path.dirname(__file__), 'bands_blacklist.txt')) as f:    
        blacklist = set([l.strip() for l in f.read().split(u'\n')])

    print('Filtering blacklist...')
    whitelisted_bands = [b for b in bands if b.name not in blacklist]
    print(f'Left with {len(whitelisted_bands)} after filtering')

    table = []
    for e in events:
        table.append({
            '!!!': '!!!' if e.is_interesting(whitelisted_bands) else '',
            'Title': e.title.title(),
            'Date': e.dt.strftime('%a, %d.%m.%Y %H:%M')
        })

    print("Events:")
    print(tabulate.tabulate(table, headers='keys', tablefmt='github'))
