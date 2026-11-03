import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.geo import haversine_distance, route_match_score, proximity_score


def test_haversine_zero_distance():
    d = haversine_distance(12.97, 77.59, 12.97, 77.59)
    assert d == 0


def test_haversine_known_distance():
    # Koramangala to Whitefield, Bengaluru ~ 14-16 km
    d = haversine_distance(12.9352, 77.6245, 12.9698, 77.7500)
    assert 10 < d < 20


def test_route_match_perfect_overlap():
    src = (12.9, 77.6)
    dst = (13.0, 77.7)
    score = route_match_score(src, dst, src, dst)
    assert score == 1.0


def test_route_match_far_detour():
    driver_src = (12.9, 77.6)
    driver_dst = (13.0, 77.7)
    rider_src = (10.0, 75.0)
    rider_dst = (11.0, 76.0)
    score = route_match_score(driver_src, driver_dst, rider_src, rider_dst)
    assert score == 0.0


def test_proximity_score_bounds():
    assert proximity_score(12.9, 77.6, 12.9, 77.6) == 1.0
    far_score = proximity_score(12.9, 77.6, 20.0, 80.0)
    assert far_score == 0.0


if __name__ == "__main__":
    test_haversine_zero_distance()
    test_haversine_known_distance()
    test_route_match_perfect_overlap()
    test_route_match_far_detour()
    test_proximity_score_bounds()
    print("All geo tests passed.")
