# coding: utf-8
import json
import random
import time
from urllib.parse import quote

import requests
from .data import BandsInTownEvent


def check_bands(bands, email):
    result = []
    bands_to_check = bands
    bands_to_retry = []
    retries = 5

    while True:
        for b in bands_to_check:
            print(f'Checking band "{b.name}"...')
            encoded_name = quote(b.name)
            url = f'https://rest.bandsintown.com/artists/{encoded_name}/events'

            params = {'api_version': '3.0', 'app_id': f'sirg-parser-3({email})'}
            resp = requests.get(url, params=params)
            if resp.status_code in {403, 404}:
                print(f'Response {resp.status_code}: band={b}, url={url}')
                continue

            try:
                print(f'Response: {resp.text[:100].strip()}')

                if '{warn=Not found}' in resp.text or '"errorMessage": "[NotFound]' in resp.text:
                    print(f'Not found: {b}')
                    continue

                rj = json.loads(resp.text)
                if isinstance(rj, dict) and u'Rate limit exceeded' in rj.get('errors', []):
                    print(f'Got rate limited on {b}')
                    bands_to_retry.append(b)
                    time.sleep(random.choice(range(10)))
                    continue

                for concert in rj:
                    try:
                        country = concert['venue']['country']
                        city = concert['venue']['city']
                        title = concert['venue']['name']
                        datetime = concert['datetime']
                    except KeyError as e:
                        print(f'Got a KeyError {e} checking {concert}')
                        continue

                    result.append(
                        BandsInTownEvent(
                            title=title,
                            bands=b,
                            dt=datetime,
                            country=country,
                            city=city,
                        )
                    )
            except json.decoder.JSONDecodeError as e:
                print(f'Got a json decode error on {b}, skipping')
                continue

            except Exception as e:
                print(f'Got an error {type(e)}: {e}')
                bands_to_retry.append(b)

        if bands_to_retry:
            print(f'Have {len(bands_to_retry)} bands to retry, taking a break before a new round')
            time.sleep(random.choice(range(10)))
            bands_to_check = bands_to_retry
            bands_to_retry = []
            if retries:
                retries -= 1
            else:
                print('No retries left')
                break
        else:
            break

    return result
