"""
TLE-to-state-vector helpers built around SGP4.

What this module does:
- Turns a TLE epoch (YYDDD.DDDDDD) into a Python datetime.
- Converts a datetime into the (jd, fr) pair SGP4 expects.
- Propagates a satellite’s position and velocity a given number of minutes from its TLE epoch.

"""

from datetime import datetime, timedelta
from tle_fetcher import SatelliteTLE, fetch_tle
from sgp4.api import Satrec
from sgp4.api import jday


def tle_epoch_to_datetime(epoch: float) -> datetime:
    """Convert a TLE epoch (YYDDD.DDDDDD) into a naive datetime.

    The format is:
      - YY: two-digit year (here interpreted as 2000–2099).
      - DDD.DDDDDD: day-of-year with fractional day.
    Example: 24320.123456 -> year=2024, 320.123456 days after Jan 1.

    Returns a naive datetime representing the same instant (effectively UTC).
    """
    year_short = int(epoch // 1000)  # e.g., 24 for 2024

    # Day-of-year including the fractional day part
    day_of_year = epoch % 1000

    # Interpret two-digit years in the 2000–2099 range
    year = 2000 + year_short

    base = datetime(year, 1, 1)
    # timedelta handles the fractional day cleanly
    dt = base + timedelta(days=day_of_year)

    return dt

def datetime_to_jday(dt: datetime) -> tuple[float, float]:
    """Convert a datetime to the (jd, fr) tuple required by Satrec.sgp4.

    sgp4 expects the Julian day split into whole and fractional parts.
    jday(year, month, day, hour, minute, seconds_with_fraction) returns (jd, fr).
    """
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    second = dt.second
    microsecond = dt.microsecond
    # Combine microseconds into the seconds value as a fractional component
    second = second + microsecond / 1_000_000
    return jday(year, month, day, hour, minute, second)

def propagate(sat: SatelliteTLE, tsince_minutes) -> tuple:
    """Propagate a satellite to a time offset from its TLE epoch.

    Args:
        sat: SatelliteTLE object with line1 and line2 strings.
        tsince_minutes: Minutes since TLE epoch at which to compute state.

    Returns:
        (position_km, velocity_km_s) where:
          - position_km is a 3-element list [x, y, z] in TEME frame (kilometers)
          - velocity_km_s is a 3-element list [vx, vy, vz] in TEME frame (km/s)

    Raises:
        ValueError: If sgp4 reports a non-zero error code.
    """
    # Per TLE convention, the epoch is in line 1, columns 19–32 (0-based slice [18:32])
    extract_epoch = float(sat.line1[18:32])
    dt_epoch = tle_epoch_to_datetime(extract_epoch)

    # Target time = epoch + tsince
    tsince = timedelta(minutes=tsince_minutes)
    dt_tsince = dt_epoch + tsince

    # Convert to Julian day components for SGP4
    jday_tsince = datetime_to_jday(dt_tsince)

    # Construct the SGP4 record and propagate
    satrec = Satrec.twoline2rv(sat.line1, sat.line2)
    error_code, position, velocity = satrec.sgp4(jday_tsince[0], jday_tsince[1])

    if error_code != 0:
        # Refer to sgp4 documentation for detailed error meanings
        raise ValueError(f"Error code: {error_code}")

    return position, velocity



# Example: fetch the ISS TLE and print its epoch as a datetime.
# Note: fetch_tle() makes a network call; avoid running this in hot paths.
"""
Keeping test commented out for now. Will move later.

tle_data = fetch_tle()
tles = tle_data["ISS (ZARYA)"]
epoch_str = tles.line1[18:32]
epoch = float(epoch_str)

dt = tle_epoch_to_datetime(epoch)
print(dt)

"""