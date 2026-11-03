# 🚗 AI Carpool Matching System

A full-stack carpool/ride-pooling web app built with **Streamlit**, combining
**K-Means clustering** with a weighted **AI-based match-scoring algorithm** to
pair riders with the best available drivers.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Login / Signup | Rider, driver, and admin roles with hashed passwords |
| 🤖 K-Means Clustering | Groups active rides into geographic zones (`scikit-learn`) to narrow the search space |
| 🧠 AI Match Score | Weighted 0–100 score combining route match, time compatibility, proximity, seats, and driver rating |
| 📍 Haversine Distance | Accurate great-circle distance calculation between coordinates |
| 🛣️ Route Matching | Detects how much a driver would detour to serve a rider's trip |
| 🕐 Time Compatibility | Scores how close ride & request departure times are |
| 💺 Seat Availability | Filters/scores based on remaining seats |
| ⭐ Driver Rating | Rolling average rating factored into the match score |
| 🎫 Ride Booking + OTP | 4-digit OTP generated per booking, verified by the rider at pickup |
| 📜 Ride History | Full booking history for riders and drivers, plus post-ride ratings |
| 🗺️ Map Display | Visualizes pickup/drop points of all active rides |
| ⚙️ Admin Dashboard | Platform-wide stats, users, rides, and bookings tables |
| 🗄️ SQLite Database | Zero-config relational storage (`data/carpool.db`) |
| 📊 cdata.xlsx | Bundled sample dataset (drivers, riders, cities) used to seed the DB |
| 🧪 Test Suite | Unit tests for geo, clustering, and matching modules |

---

## 🗂️ Project Structure

```
carpool_app/
├── app.py                     # Main Streamlit entry point (login/signup + dashboard)
├── pages/
│   ├── 1_Find_a_Ride.py       # Rider search + AI-ranked matches + booking
│   ├── 2_Offer_a_Ride.py      # Driver ride posting + management
│   ├── 3_My_Bookings.py       # Ride history, OTP verification, ratings
│   ├── 4_Map_View.py          # Map of active rides
│   └── 5_Admin_Dashboard.py   # Admin-only platform overview
├── utils/
│   ├── db.py                  # SQLite schema + all CRUD operations
│   ├── geo.py                 # Haversine distance + route matching
│   ├── clustering.py          # K-Means zone clustering
│   ├── matching.py            # Weighted AI match-score algorithm
│   ├── geocode.py             # Offline place-name -> lat/lon lookup
│   ├── auth.py                # Password hashing, login/signup
│   └── seed.py                # Seeds the DB from data/cdata.xlsx on first run
├── data/
│   ├── cities.csv             # Bengaluru locality coordinates (offline geocoder)
│   ├── cdata.xlsx             # Sample dataset: drivers, riders, cities (3 sheets)
│   ├── generate_cdata.py      # Script that (re)generates cdata.xlsx
│   └── carpool.db             # SQLite DB (created automatically on first run)
├── tests/
│   ├── test_geo.py
│   ├── test_clustering.py
│   └── test_matching.py
├── requirements.txt
└── README.md
```

---

## 🧠 How the Matching Algorithm Works

1. **K-Means Clustering (`utils/clustering.py`)**
   All active rides' pickup coordinates are clustered into `k` geographic
   zones using `sklearn.cluster.KMeans`. When a rider searches, their pickup
   point is assigned to the nearest zone(s), narrowing the search from *all*
   rides to just the nearby ones — this is what makes the system scale.

2. **AI Match Score (`utils/matching.py`)**
   Every candidate ride in the narrowed pool is scored against the rider's
   request using a weighted formula:

   ```
   score = 0.35 × route_match
         + 0.25 × time_compatibility
         + 0.20 × pickup_proximity
         + 0.10 × seat_availability
         + 0.10 × driver_rating
   ```

   - **Route Match** — computed from `utils/geo.py`'s `route_deviation_score`:
     the extra distance a driver would travel by detouring through the
     rider's pickup/drop vs. going straight to their own destination.
   - **Time Compatibility** — linear decay based on the gap (in minutes)
     between the ride's departure time and the rider's preferred time.
   - **Pickup Proximity** — Haversine distance between the rider's pickup
     point and the driver's starting point.
   - **Seat Availability** — binary: enough seats or not.
   - **Driver Rating** — normalized 0–5 star rating.

   Results are sorted descending and only matches scoring ≥ 20% are shown,
   with a full breakdown displayed to the user for transparency.

---

## ⚙️ Setup & Installation

### 1. Requirements
- Python 3.9+

### 2. Install dependencies
```bash
cd carpool_app
pip install -r requirements.txt
```

### 3. (Optional) Regenerate the sample dataset
The repo already ships with `data/cdata.xlsx`. To regenerate it:
```bash
python data/generate_cdata.py
```

### 4. Run the app
```bash
streamlit run app.py
```
The SQLite database (`data/carpool.db`) is created and auto-seeded from
`cdata.xlsx` the first time you run the app.

### 5. Demo accounts
All seeded accounts use the password **`password123`**:
- Admin: `admin@carpool.com`
- Driver: `driver1@example.com` … `driver20@example.com`
- Rider: `rider1@example.com` … `rider30@example.com`

### 6. Run tests
```bash
python tests/test_geo.py
python tests/test_clustering.py
python tests/test_matching.py
```

---

## 🛣️ Roadmap / Ideas for Extension
- Replace the offline CSV geocoder with a real geocoding API (Google/Mapbox) for any city
- Add real-time driver location tracking with `streamlit-autorefresh`
- Push notifications for match alerts (email/SMS OTP instead of on-screen)
- Payment gateway integration for fare settlement
- Swap SQLite for PostgreSQL for multi-user production deployment

---

## 📄 License
This project is provided as a educational/demo template — adapt freely for your own use.
