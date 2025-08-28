from tle_fetcher import fetch_tle, SatelliteTLE
from propagate import propagate

"""
Temporary test for propagate.py in order to print results to console.
"""
tles = fetch_tle()
iss = tles["ISS (ZARYA)"]
postition, velocity = propagate(iss, tsince_minutes=0.0)

print("Postiion (km):", postition)
print("Velocity (km/s):", velocity)
