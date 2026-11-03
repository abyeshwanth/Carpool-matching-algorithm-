"""
db.py - SQLite database layer for the Carpool Matching App.
Handles schema creation and all CRUD operations.
"""

import sqlite3
import os
import random
import string
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "carpool.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create all tables if they do not already exist."""
    with get_conn() as conn:
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            role TEXT NOT NULL DEFAULT 'rider',   -- 'rider', 'driver', 'admin'
            rating REAL DEFAULT 5.0,
            rating_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            source_lat REAL NOT NULL,
            source_lon REAL NOT NULL,
            dest_lat REAL NOT NULL,
            dest_lon REAL NOT NULL,
            ride_date TEXT NOT NULL,
            ride_time TEXT NOT NULL,
            total_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            price_per_seat REAL DEFAULT 0,
            status TEXT DEFAULT 'active',   -- active, completed, cancelled
            cluster_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (driver_id) REFERENCES users(id)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS ride_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rider_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            source_lat REAL NOT NULL,
            source_lon REAL NOT NULL,
            dest_lat REAL NOT NULL,
            dest_lon REAL NOT NULL,
            ride_date TEXT NOT NULL,
            ride_time TEXT NOT NULL,
            seats_needed INTEGER DEFAULT 1,
            status TEXT DEFAULT 'pending',   -- pending, matched, cancelled
            cluster_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rider_id) REFERENCES users(id)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ride_id INTEGER NOT NULL,
            rider_id INTEGER NOT NULL,
            request_id INTEGER,
            seats_booked INTEGER DEFAULT 1,
            match_score REAL,
            otp TEXT,
            otp_verified INTEGER DEFAULT 0,
            status TEXT DEFAULT 'booked',   -- booked, completed, cancelled
            booked_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ride_id) REFERENCES rides(id),
            FOREIGN KEY (rider_id) REFERENCES users(id)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            rater_id INTEGER NOT NULL,
            ratee_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            comment TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
        """)
        conn.commit()


# ---------------------------------------------------------------- users ----
def create_user(name, email, password, phone, role="rider"):
    with get_conn() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO users (name, email, password, phone, role) VALUES (?,?,?,?,?)",
                (name, email, password, phone, role),
            )
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None


def get_user_by_email(email):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(uid):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        return dict(row) if row else None


def update_user_rating(user_id, new_score):
    with get_conn() as conn:
        row = conn.execute("SELECT rating, rating_count FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            return
        old_avg, count = row["rating"], row["rating_count"]
        new_count = count + 1
        new_avg = ((old_avg * count) + new_score) / new_count
        conn.execute("UPDATE users SET rating=?, rating_count=? WHERE id=?", (new_avg, new_count, user_id))


# ---------------------------------------------------------------- rides ----
def create_ride(driver_id, source, destination, source_lat, source_lon, dest_lat, dest_lon,
                 ride_date, ride_time, total_seats, price_per_seat=0):
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO rides (driver_id, source, destination, source_lat, source_lon,
                                dest_lat, dest_lon, ride_date, ride_time, total_seats,
                                available_seats, price_per_seat)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (driver_id, source, destination, source_lat, source_lon, dest_lat, dest_lon,
              ride_date, ride_time, total_seats, total_seats, price_per_seat))
        return cur.lastrowid


def get_active_rides():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT rides.*, users.name AS driver_name, users.rating AS driver_rating,
                   users.phone AS driver_phone
            FROM rides JOIN users ON rides.driver_id = users.id
            WHERE rides.status='active' AND rides.available_seats > 0
            ORDER BY rides.ride_date, rides.ride_time
        """).fetchall()
        return [dict(r) for r in rows]


def get_ride(ride_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM rides WHERE id=?", (ride_id,)).fetchone()
        return dict(row) if row else None


def get_rides_by_driver(driver_id):
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM rides WHERE driver_id=? ORDER BY created_at DESC", (driver_id,)).fetchall()
        return [dict(r) for r in rows]


def update_ride_cluster(ride_id, cluster_id):
    with get_conn() as conn:
        conn.execute("UPDATE rides SET cluster_id=? WHERE id=?", (cluster_id, ride_id))


def decrement_seats(ride_id, seats):
    with get_conn() as conn:
        conn.execute("UPDATE rides SET available_seats = available_seats - ? WHERE id=?", (seats, ride_id))


def cancel_ride(ride_id):
    with get_conn() as conn:
        conn.execute("UPDATE rides SET status='cancelled' WHERE id=?", (ride_id,))


# -------------------------------------------------------------- requests --
def create_request(rider_id, source, destination, source_lat, source_lon, dest_lat, dest_lon,
                    ride_date, ride_time, seats_needed=1):
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO ride_requests (rider_id, source, destination, source_lat, source_lon,
                                        dest_lat, dest_lon, ride_date, ride_time, seats_needed)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (rider_id, source, destination, source_lat, source_lon, dest_lat, dest_lon,
              ride_date, ride_time, seats_needed))
        return cur.lastrowid


def update_request_cluster(request_id, cluster_id):
    with get_conn() as conn:
        conn.execute("UPDATE ride_requests SET cluster_id=? WHERE id=?", (cluster_id, request_id))


def get_all_requests():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM ride_requests WHERE status='pending'").fetchall()
        return [dict(r) for r in rows]


# -------------------------------------------------------------- bookings --
def generate_otp():
    return "".join(random.choices(string.digits, k=4))


def create_booking(ride_id, rider_id, seats_booked, match_score, request_id=None):
    otp = generate_otp()
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO bookings (ride_id, rider_id, request_id, seats_booked, match_score, otp)
            VALUES (?,?,?,?,?,?)
        """, (ride_id, rider_id, request_id, seats_booked, match_score, otp))
        booking_id = cur.lastrowid
    decrement_seats(ride_id, seats_booked)
    if request_id:
        with get_conn() as conn:
            conn.execute("UPDATE ride_requests SET status='matched' WHERE id=?", (request_id,))
    return booking_id, otp


def verify_otp(booking_id, otp_input):
    with get_conn() as conn:
        row = conn.execute("SELECT otp FROM bookings WHERE id=?", (booking_id,)).fetchone()
        if row and row["otp"] == otp_input:
            conn.execute("UPDATE bookings SET otp_verified=1, status='completed' WHERE id=?", (booking_id,))
            return True
        return False


def get_bookings_by_rider(rider_id):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT bookings.*, rides.source, rides.destination, rides.ride_date, rides.ride_time,
                   rides.driver_id, users.name AS driver_name
            FROM bookings
            JOIN rides ON bookings.ride_id = rides.id
            JOIN users ON rides.driver_id = users.id
            WHERE bookings.rider_id=?
            ORDER BY bookings.booked_at DESC
        """, (rider_id,)).fetchall()
        return [dict(r) for r in rows]


def get_bookings_for_driver(driver_id):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT bookings.*, rides.source, rides.destination, rides.ride_date, rides.ride_time,
                   users.name AS rider_name, users.phone AS rider_phone
            FROM bookings
            JOIN rides ON bookings.ride_id = rides.id
            JOIN users ON bookings.rider_id = users.id
            WHERE rides.driver_id=?
            ORDER BY bookings.booked_at DESC
        """, (driver_id,)).fetchall()
        return [dict(r) for r in rows]


def add_rating(booking_id, rater_id, ratee_id, score, comment=""):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO ratings (booking_id, rater_id, ratee_id, score, comment)
            VALUES (?,?,?,?,?)
        """, (booking_id, rater_id, ratee_id, score, comment))
    update_user_rating(ratee_id, score)


# ---------------------------------------------------------------- admin ---
def get_all_users():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name, email, phone, role, rating, rating_count, created_at FROM users").fetchall()
        return [dict(r) for r in rows]


def get_all_rides():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT rides.*, users.name AS driver_name FROM rides
            JOIN users ON rides.driver_id = users.id
            ORDER BY rides.created_at DESC
        """).fetchall()
        return [dict(r) for r in rows]


def get_all_bookings():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT bookings.*, rides.source, rides.destination, u1.name AS rider_name,
                   u2.name AS driver_name
            FROM bookings
            JOIN rides ON bookings.ride_id = rides.id
            JOIN users u1 ON bookings.rider_id = u1.id
            JOIN users u2 ON rides.driver_id = u2.id
            ORDER BY bookings.booked_at DESC
        """).fetchall()
        return [dict(r) for r in rows]


def get_stats():
    with get_conn() as conn:
        users = conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
        rides = conn.execute("SELECT COUNT(*) c FROM rides").fetchone()["c"]
        bookings = conn.execute("SELECT COUNT(*) c FROM bookings").fetchone()["c"]
        active_rides = conn.execute("SELECT COUNT(*) c FROM rides WHERE status='active'").fetchone()["c"]
        return {"users": users, "rides": rides, "bookings": bookings, "active_rides": active_rides}
