"""
generate_cdata.py - Builds data/cdata.xlsx, a sample dataset of drivers,
riders and rides used to seed the database (see utils/seed.py) and for
offline testing of the clustering/matching algorithms.

Run once:  python data/generate_cdata.py
"""

import pandas as pd
import os
import random

random.seed(42)
HERE = os.path.dirname(__file__)

cities = pd.read_csv(os.path.join(HERE, "cities.csv"))
places = cities.to_dict("records")

FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
               "Ishaan", "Rohan", "Ananya", "Diya", "Priya", "Isha", "Kavya", "Meera",
               "Neha", "Riya", "Sneha", "Tanvi"]
LAST_NAMES = ["Sharma", "Verma", "Iyer", "Reddy", "Gupta", "Nair", "Rao", "Menon",
              "Kumar", "Singh", "Patel", "Joshi"]


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_phone():
    return "9" + "".join(str(random.randint(0, 9)) for _ in range(9))


# ---- Drivers sheet ----
drivers = []
for i in range(1, 21):
    src, dst = random.sample(places, 2)
    drivers.append({
        "driver_id": i,
        "name": random_name(),
        "email": f"driver{i}@example.com",
        "phone": random_phone(),
        "source": src["place"],
        "source_lat": src["lat"],
        "source_lon": src["lon"],
        "destination": dst["place"],
        "dest_lat": dst["lat"],
        "dest_lon": dst["lon"],
        "ride_date": "2025-09-0" + str(random.randint(1, 9)),
        "ride_time": f"{random.randint(6,20):02d}:{random.choice(['00','15','30','45'])}",
        "total_seats": random.randint(2, 4),
        "price_per_seat": random.choice([50, 75, 100, 120, 150]),
        "rating": round(random.uniform(3.5, 5.0), 1),
    })

# ---- Riders / requests sheet ----
riders = []
for i in range(1, 31):
    src, dst = random.sample(places, 2)
    riders.append({
        "rider_id": i,
        "name": random_name(),
        "email": f"rider{i}@example.com",
        "phone": random_phone(),
        "source": src["place"],
        "source_lat": src["lat"],
        "source_lon": src["lon"],
        "destination": dst["place"],
        "dest_lat": dst["lat"],
        "dest_lon": dst["lon"],
        "ride_date": "2025-09-0" + str(random.randint(1, 9)),
        "ride_time": f"{random.randint(6,20):02d}:{random.choice(['00','15','30','45'])}",
        "seats_needed": random.choice([1, 1, 1, 2]),
    })

df_drivers = pd.DataFrame(drivers)
df_riders = pd.DataFrame(riders)
df_cities = cities

out_path = os.path.join(HERE, "cdata.xlsx")
with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
    df_drivers.to_excel(writer, sheet_name="drivers", index=False)
    df_riders.to_excel(writer, sheet_name="riders", index=False)
    df_cities.to_excel(writer, sheet_name="cities", index=False)

print(f"cdata.xlsx generated at {out_path}")
