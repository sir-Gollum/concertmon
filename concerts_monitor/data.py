# coding: utf-8
import datetime


class Band(object):
    def __init__(self, name: str, playcount: int):
        self.name = name
        self.lname = name.lower()
        self.playcount = playcount

    def __str__(self):
        return f'<{self.name}, pc: {self.playcount}>'


class Event(object):
    def __init__(self, title: str, bands: str, dt: str, country: str='Germany', city: str='Munich'):
        self.title = title
        self.bands = bands
        self.country = country
        self.city = city
        self.dt = self.parse_datetime(dt)

    def parse_datetime(self, dt):
        raise NotImplementedError('Should be implemented in a child class')

    def __str__(self):
        return f'<{self.title.title()} - {self.bands.title()} playing in {self.city} at {self.dt}>'

    def __repr__(self):
        return self.__str__()


class BackstageEvent(Event):
    def is_interesting(self, favourite_bands):
        ltb = self.title.lower() + self.bands.lower()
        # TODO: fuzzy match, mark matching substring with color etc.
        for b in favourite_bands:
            if b.lname in ltb:
                return True
        return False

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
        ltb = self.title.lower() + self.bands.lower()
        lc = self.country.lower()
        lcities = [c.lower() for c in cities]
        lcountries = [c.lower() for c in countries]

        if lcountries:
            if (
                any(c in lc for c in lcountries)
                or any(c in ltb for c in lcities)
            ):
                return True
        else:
            if any(c in ltb for c in lcities):
                return True

        return False


