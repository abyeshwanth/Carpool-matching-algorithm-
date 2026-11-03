"""
geocode.py - Lightweight offline "geocoder".

For a self-contained demo/professional-project setup we ship a small table
of well-known Indian city localities (data/cities.csv) instead of depending
on a paid/external geocoding API. This keeps the app fully runnable offline.
"""

import pandas as pd
import os

CITIES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cities.csv")

_df_cache = None


def _load():
    global _df_cache
    if _df_cache is None:
        _df_cache = pd.read_csv(CITIES_PATH)
    return _df_cache


def get_all_places():
    df = _load()
    return df["place"].tolist()


def geocode(place_name):
    """Return (lat, lon) for a known place name, or (None, None)."""
    df = _load()
    row = df[df["place"].str.lower() == place_name.lower()]
    if row.empty:
        return None, None
    return float(row.iloc[0]["lat"]), float(row.iloc[0]["lon"])
