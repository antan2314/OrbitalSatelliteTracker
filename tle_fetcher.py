from dataclasses import dataclass

import requests

r = requests.get('https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle')


@dataclass
class SatelliteTLE:
    name: str
    line1: str
    line2: str


def fetch_tle() ->dict[str, SatelliteTLE]:
    lines = r.text.splitlines()
    if len(lines) % 3 != 0:
        raise ValueError('TLE does not have enough lines')
    tle = {}
    for i in range(0, len(lines), 3):

        name = lines[i].strip()
        line1 = lines[i+1]
        line2 = lines[i+2]

        s = SatelliteTLE(name=name, line1=line1, line2=line2)
        tle[name] = s
    return tle
