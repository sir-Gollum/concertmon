# coding: utf-8
import time

import requests
from lxml import html
import tabulate
import random
from .data import BackstageEvent


def _get_page_events(html_content: str):
    result = []
    tree = html.fromstring(html_content)

    for pid in tree.xpath('//*[@class="product-item-info" and @id]'):
        details_items = [it.strip() for it in pid.xpath('.//h6/text()')]
        details = ' '.join([
            di for di in details_items
            if di and not di.lower().startswith('presented by')
        ])
        details = ' '.join(details.split())

        title_bands = pid.xpath('string(.//strong/a)').strip()
        venue = pid.xpath('string(.//*[contains(@class, "eventlocation")])').strip()
        link = pid.xpath('.//strong/a/@href')[0]

        date_str = None
        for dt_elem in pid.xpath('.//*[contains(@class, "eventdate")]'):
            day_elem = dt_elem.xpath('.//*[contains(@class, "day")]')[0]
            if 'text-decoration: line-through' in day_elem.get('style', ''):
                continue

            mon_elem = dt_elem.xpath('.//*[contains(@class, "month")]')[0]
            year_elem = dt_elem.xpath('.//*[contains(@class, "year")]')[0]

            event_date_str = ' '.join([
                day_elem.text.strip(),
                mon_elem.text.strip(),
                year_elem.text.strip()
            ])

            if date_str:
                print(f'Warning: multiple dates for {title_bands}: {date_str} and {event_date_str}')
            date_str = event_date_str

        event = BackstageEvent(
            title=title_bands,
            bands=title_bands,
            venue=venue,
            dt=date_str,
            link=link,
            details=details,
        )

        if event.dt is None:
            # Drop cancelled events
            print(f'Warning: no date for {event}')
            continue

        result.append(event)

    return result


def _get_page(page_number: int):
    url = 'https://backstage.eu/veranstaltungen/live.html'
    params = {'product_list_limit': 25}
    if page_number > 1:
        params.update({
            'p': page_number,
            'scrollAjax': 1,
        })

    print(f'Getting Backstage info with params {params}')
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f'Bad status on backstage crawl with params {params}: {response.status_code}')
        return []

    return response


def get_backstage_events(page_limit=None):
    response = _get_page(1)
    result = _get_page_events(response.text)

    is_last = False
    page_number = 2
    while not is_last:
        time.sleep(3 + random.random() * 2)
        response = _get_page(page_number)
        rjson = response.json()
        is_last = rjson['isLast']
        page_number += 1
        result += _get_page_events(rjson['html']['products'])

        if page_limit and page_number > page_limit:
            break

    return result


def sort_and_deduplicate_events(events):
    events = sorted(events, key=lambda e: (e.dt, e.title, e.bands))
    result = []
    for e in events:
        if result and str(e) == str(result[-1]):
            continue
        result.append(e)
    return result


if __name__ == '__main__':
    events = sort_and_deduplicate_events(get_backstage_events(4))
    print(f'Got {len(events)} events')

    table = []
    for e in events:
        table.append({
            'Title': e.title.title(),
            'Date': e.dt.strftime('%a, %d.%m.%Y %H:%M'),
            'Link': e.link,
            'Venue': e.venue,
            'Details': e.details,
        })

    print("Events:")
    print(tabulate.tabulate(table, headers='keys', tablefmt='github'))
