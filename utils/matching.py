"""
matching.py - The core carpool matching algorithm.

Combines several weighted sub-scores into a single 0-100 "AI Match Score":

    1. Route Match       (35%) - how well the rider's trip overlaps the driver's route
    2. Time Compatibility(25%) - how close the requested time is to the ride's departure
    3. Pickup Proximity  (20%) - haversine distance between rider & driver source points
    4. Seat Availability (10%) - whether enough seats remain
    5. Driver Rating     (10%) - normalized driver star rating

K-Means clustering (see clustering.py) is used upstream to narrow the
candidate pool to the same/nearby geographic zone before this fine-grained
scoring function is applied - this keeps the algorithm fast (no need to
score every ride in the database) while the weighted formula gives an
explainable, tunable "AI-based" ranking.
"""

from datetime import datetime
from utils.geo import route_match_score, proximity_score, haversine_distance

WEIGHTS = {
    "route": 0.35,
    "time": 0.25,
    "proximity": 0.20,
    "seats": 0.10,
    "rating": 0.10,
}


def time_compatibility_score(ride_date, ride_time, req_date, req_time, max_gap_minutes=60):
    """
    Score based on how close the ride's departure time is to the rider's
    requested time. 1.0 = same time, 0.0 = gap >= max_gap_minutes.
    Dates must match exactly (different day => 0 score).
    """
    if ride_date != req_date:
        return 0.0

    fmt = "%H:%M"
    try:
        t1 = datetime.strptime(ride_time, fmt)
        t2 = datetime.strptime(req_time, fmt)
    except ValueError:
        return 0.0

    gap_minutes = abs((t1 - t2).total_seconds()) / 60
    score = max(0.0, 1 - (gap_minutes / max_gap_minutes))
    return round(score, 4)


def seat_score(available_seats, seats_needed):
    if available_seats >= seats_needed:
        return 1.0
    return 0.0


def rating_score(driver_rating, max_rating=5.0):
    return round(min(driver_rating / max_rating, 1.0), 4)


def compute_match_score(ride, request):
    """
    Compute the composite AI match score (0-100) between a ride (driver offer)
    and a ride_request (rider's need). `ride` and `request` are dicts as
    returned from db.py.
    """
    driver_src = (ride["source_lat"], ride["source_lon"])
    driver_dst = (ride["dest_lat"], ride["dest_lon"])
    rider_src = (request["source_lat"], request["source_lon"])
    rider_dst = (request["dest_lat"], request["dest_lon"])

    r_score = route_match_score(driver_src, driver_dst, rider_src, rider_dst)
    t_score = time_compatibility_score(ride["ride_date"], ride["ride_time"],
                                        request["ride_date"], request["ride_time"])
    p_score = proximity_score(*driver_src, *rider_src)
    s_score = seat_score(ride["available_seats"], request.get("seats_needed", 1))
    rt_score = rating_score(ride.get("driver_rating", 5.0))

    total = (
        r_score * WEIGHTS["route"]
        + t_score * WEIGHTS["time"]
        + p_score * WEIGHTS["proximity"]
        + s_score * WEIGHTS["seats"]
        + rt_score * WEIGHTS["rating"]
    )

    breakdown = {
        "route_match": round(r_score * 100, 1),
        "time_compatibility": round(t_score * 100, 1),
        "pickup_proximity": round(p_score * 100, 1),
        "seat_availability": round(s_score * 100, 1),
        "driver_rating": round(rt_score * 100, 1),
        "total_score": round(total * 100, 1),
    }
    return breakdown


def rank_matches(candidate_rides, request, min_score=30.0):
    """
    Score a list of candidate rides against a single request and return
    them sorted by descending match score, filtering out weak matches.
    """
    results = []
    for ride in candidate_rides:
        breakdown = compute_match_score(ride, request)
        if breakdown["total_score"] >= min_score:
            results.append({"ride": ride, "score": breakdown})
    results.sort(key=lambda x: x["score"]["total_score"], reverse=True)
    return results
