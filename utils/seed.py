"""
seed.py - Loads data/cdata.xlsx into the SQLite database so the app has
realistic demo data (drivers, riders, active rides) on first run.
"""

import pandas as pd
import os
import hashlib
from utils import db

CDATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cdata.xlsx")
DEFAULT_PASSWORD_HASH = hashlib.sha256("password123".encode()).hexdigest()


def seed_if_empty():
    db.init_db()
    stats = db.get_stats()
    if stats["users"] > 0:
        return False  # already seeded

    xls = pd.ExcelFile(CDATA_PATH)
    drivers_df = pd.read_excel(xls, "drivers")
    riders_df = pd.read_excel(xls, "riders")

    # Admin account
    db.create_user("Admin", "admin@carpool.com", DEFAULT_PASSWORD_HASH, "9000000000", role="admin")

    driver_id_map = {}
    for _, row in drivers_df.iterrows():
        uid = db.create_user(row["name"], row["email"], DEFAULT_PASSWORD_HASH, str(row["phone"]), role="driver")
        if uid is None:
            continue
        driver_id_map[row["driver_id"]] = uid
        ride_id = db.create_ride(
            driver_id=uid,
            source=row["source"], destination=row["destination"],
            source_lat=row["source_lat"], source_lon=row["source_lon"],
            dest_lat=row["dest_lat"], dest_lon=row["dest_lon"],
            ride_date=str(row["ride_date"]), ride_time=str(row["ride_time"]),
            total_seats=int(row["total_seats"]), price_per_seat=float(row["price_per_seat"]),
        )
        # Bump driver rating to match the sample dataset
        db.update_user_rating(uid, float(row["rating"]))

    for _, row in riders_df.iterrows():
        uid = db.create_user(row["name"], row["email"], DEFAULT_PASSWORD_HASH, str(row["phone"]), role="rider")
        if uid is None:
            continue
        db.create_request(
            rider_id=uid,
            source=row["source"], destination=row["destination"],
            source_lat=row["source_lat"], source_lon=row["source_lon"],
            dest_lat=row["dest_lat"], dest_lon=row["dest_lon"],
            ride_date=str(row["ride_date"]), ride_time=str(row["ride_time"]),
            seats_needed=int(row["seats_needed"]),
        )

    return True
