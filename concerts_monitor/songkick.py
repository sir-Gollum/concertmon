# coding: utf-8
import json
import time

import requests
from .data import SongkickEvent


def check_bands(bands, api_key):
    result = []

    for b in bands:
        print(f'Checking Sonkick for band "{b.name}"...')
        url = 'https://api.songkick.com/api/3.0/events.json'

        errors = 0
        for page in range(1, 100):
            params = {'artist_name': b.name, 'page': page, 'apikey': api_key}

            resp = requests.get(url, params=params)

            if resp.status_code != 200:
                print(f'Response {resp.status_code}: band={b}, url={url}: {resp.text}')
                time.sleep(1.1)
                errors += 1
                if errors > 1:
                    break
                continue

            try:
                print(f'Response: {resp.text[:100].strip()}')
                rj = json.loads(resp.text)

                if rj['resultsPage']['status'] != 'ok':
                    print(f"Bad status: {rj['resultsPage']['status']}")
                    continue

                if not rj['resultsPage']['results']:
                    print('Empty result')
                    break

                for concert in rj['resultsPage']['results']['event']:
                    country = concert['venue']['metroArea']['country']['displayName']
                    city = concert['location']['city'].split(',')[0]
                    title = concert['displayName']

                    datetime = concert['start']['date']
                    if concert['start']['time']:
                        datetime += f" {concert['start']['time']}"

                    result.append(
                        SongkickEvent(title=title, bands=b, dt=datetime, country=country, city=city)
                    )

                if rj['resultsPage']['perPage'] * page >= rj['resultsPage']['totalEntries']:
                    break

            except json.decoder.JSONDecodeError as e:
                print(f'Got a json decode error on {b}, skipping')
                time.sleep(1.1)
                errors += 1
                if errors > 1:
                    break
                continue

            except KeyboardInterrupt:
                print('Interrupted')
                return

            except Exception as e:
                print(f'Got an error {type(e)}: {e}')
                time.sleep(1.1)
                errors += 1
                if errors > 1:
                    break
                continue

    return result
