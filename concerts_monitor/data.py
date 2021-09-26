# coding: utf-8
import datetime
from typing import Union, List


class Band(object):
    def __init__(self, name: str, playcount: int):
        self.name = name
        self.lname = name.lower()
        self.playcount = playcount

    def __str__(self):
        return f'<{self.name}, pc: {self.playcount}>'

    def __repr__(self):
        return str(self)


class Event(object):
    def __init__(self, title: str, bands: Union[str, Band], dt: str, country: str='Germany', city: str='Munich'):
        self.title = title
        # `Band` in case of bandsintown, str in case of backstage and other similar sites where we go from events
        self.bands = bands
        self.country = country
        self.city = city
        self.dt = self.parse_datetime(dt)

    def parse_datetime(self, dt):
        raise NotImplementedError('Should be implemented in a child class')

    def __str__(self):
        return f'<{self.title.title()} - {self.bands.title()} playing in {self.city} at {self.dt}>'

    def __repr__(self):
        return str(self)


class BackstageEvent(Event):
    def match_favourite(self, favourite_bands: List[Band], top=3) -> List[Band]:
        search_str = (self.title + self.bands).lower()
        res = []

        for b in favourite_bands:
            if b.lname in search_str:
                res.append(b)

        res = sorted(res, key=lambda x: -x.playcount)

        return res[:top]

    def is_interesting(self, favourite_bands):
        return bool(self.match_favourite(favourite_bands))

    def parse_datetime(self, dt):
        result = dt
        for substr, replacement in (
            ('Montag, ', ''),
            ('Dienstag, ', ''),
            ('Mittwoch, ', ''),
            ('Donnerstag, ', ''),
            ('Freitag, ', ''),
            ('Samstag, ', ''),
            ('Sonntag, ', '',),
            ('. Januar ', '.01.'),
            ('. Februar ', '.02.'),
            ('. März ', '.03.'),
            ('. April ', '.04.'),
            ('. Mai ', '.05.'),
            ('. Juni ', '.06.'),
            ('. Juli ', '.07.'),
            ('. August ', '.08.'),
            ('. September ', '.09.'),
            ('. Oktober ', '.10.'),
            ('. November ', '.11.'),
            ('. Dezember ', '.12.'),
            ('Beginn: ', ''),
            (' Uhr', '',)
        ):
            result = result.replace(substr, replacement)
        try:
            result = datetime.datetime.strptime(result, '%d.%m.%Y %H:%M')
        except:
            print(f'Failed parsing date "{dt}". Attempted to parse "{result}"')
            result = datetime.datetime.now()
            # raise

        return result


class BandsInTownEvent(Event):
    def parse_datetime(self, dt):
        # Format: 2018-11-17T19:00:20 and we don't need seconds
        dt = dt[:-3]
        return datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M')

    def is_interesting(self, countries, cities):
        event_country = self.country.lower()
        event_city = self.city.lower()

        target_countries = [c.lower() for c in countries]
        target_cities = [c.lower() for c in cities]

        has_country_match = any(c in event_country for c in target_countries)
        has_city_match = any(c in event_city for c in target_cities)

        if target_countries and target_cities:
            return has_country_match and has_city_match

        elif target_countries:
            return has_country_match

        elif target_cities:
            return has_city_match

        return False


class SongkickEvent(BandsInTownEvent):
    def parse_datetime(self, dt):
        # Format: either '2018-11-17' or '2018-11-17 18:30:00'
        if len(dt) == len('2018-01-01'):
            return datetime.datetime.strptime(dt, '%Y-%m-%d')
        return datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
