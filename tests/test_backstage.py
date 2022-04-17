# coding: utf-8
import datetime
import os
from unittest import mock

import pytest
import responses
from concerts_monitor import backstage


def _read_fixture_file(fixture_filename):
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    with open(os.path.join(fixtures_dir, fixture_filename)) as f:
        return f.read()


@pytest.fixture
def mock_sleep():
    with mock.patch('concerts_monitor.backstage.time.sleep') as sleep:
        yield sleep


@pytest.fixture
def backstage_responses():
    with responses.RequestsMock() as rsps:
        url = 'https://backstage.eu/veranstaltungen/live.html'
        rsps.add(
            responses.GET,
            url,
            body=_read_fixture_file('backstage_page_1.html'),
            status=200,
            match=[responses.matchers.query_param_matcher({'product_list_limit': 25})],
        )
        rsps.add(
            responses.GET,
            url,
            body=_read_fixture_file('backstage_page_2.json'),
            status=200,
            match=[
                responses.matchers.query_param_matcher(
                    {
                        'product_list_limit': 25,
                        'p': 2,
                        'scrollAjax': 1,
                    }
                )
            ],
        )
        rsps.add(
            # This one is manually changeds to be the last page
            responses.GET,
            url,
            body=_read_fixture_file('backstage_page_3.json'),
            status=200,
            match=[
                responses.matchers.query_param_matcher(
                    {
                        'product_list_limit': 25,
                        'p': 3,
                        'scrollAjax': 1,
                    }
                )
            ],
        )
        yield rsps


def test_backstage_parser(backstage_responses, mock_sleep):
    found_events = backstage.get_backstage_events()
    found_event_titles = [event.title for event in found_events]
    assert len(found_events) == 60

    # non-cancelled events
    for title_should_be_present in [
        'DARK EASTER METAL MEETING  2022',
        'DARK TRANQUILITY + ENSIFERUM',
        'ELÄKELÄISET',
        'W.A.S.P.',
    ]:
        assert found_event_titles.count(title_should_be_present) == 1

    # cancelled events
    for title_cancelled in [
        'HUMANITY’S LAST BREATH',
        'PRIEST',
        'PRIEST | ABGESAGT',
    ]:
        assert title_cancelled not in found_event_titles

    # postponed events
    postponed_concert = next(it for it in found_events if it.title == 'U.D.O.')
    assert postponed_concert.dt == datetime.date(2022, 9, 4)
