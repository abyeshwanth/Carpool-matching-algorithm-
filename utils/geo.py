"""
geo.py - Geographic utility functions: Haversine distance & route matching.
"""

import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Compute the great-circle distance between two points on Earth (in km)
    using the Haversine formula.
    """
    R = 6371.0  # Earth radius in km

    lat1_r, lon1_r, lat2_r, lon2_r = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def route_deviation_score(driver_src, driver_dst, rider_src, rider_dst):
    """
    Estimate how much a driver would need to deviate from their planned route
    to pick up and drop off a rider. Returns a distance in km:
    (driver_src -> rider_src -> rider_dst -> driver_dst) - (driver_src -> driver_dst)

    Lower is better - means the rider's route lies close to the driver's path.
    """
    direct = haversine_distance(*driver_src, *driver_dst)

    via_rider = (
        haversine_distance(*driver_src, *rider_src)
        + haversine_distance(*rider_src, *rider_dst)
        + haversine_distance(*rider_dst, *driver_dst)
    )
    deviation = max(via_rider - direct, 0)
    return deviation


def route_match_score(driver_src, driver_dst, rider_src, rider_dst, max_deviation_km=10):
    """
    Convert route deviation into a normalized score between 0 and 1.
    1.0 = perfect route overlap, 0.0 = deviation >= max_deviation_km.
    """
    deviation = route_deviation_score(driver_src, driver_dst, rider_src, rider_dst)
    score = max(0.0, 1 - (deviation / max_deviation_km))
    return round(score, 4)


def proximity_score(lat1, lon1, lat2, lon2, max_km=5):
    """
    Score for how close two points are (e.g. rider pickup vs driver source).
    1.0 = same point, 0.0 = max_km or farther apart.
    """
    dist = haversine_distance(lat1, lon1, lat2, lon2)
    score = max(0.0, 1 - (dist / max_km))
    return round(score, 4)
