import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.matching import compute_match_score, time_compatibility_score, seat_score, rating_score


def sample_ride():
    return {
        "source_lat": 12.9352, "source_lon": 77.6245,   # Koramangala
        "dest_lat": 12.9698, "dest_lon": 77.7500,        # Whitefield
        "ride_date": "2025-09-05", "ride_time": "09:00",
        "available_seats": 3, "driver_rating": 4.5,
    }


def sample_request(offset_minutes=0, seats=1):
    return {
        "source_lat": 12.9352, "source_lon": 77.6245,
        "dest_lat": 12.9698, "dest_lon": 77.7500,
        "ride_date": "2025-09-05", "ride_time": "09:00",
        "seats_needed": seats,
    }


def test_perfect_match_high_score():
    ride = sample_ride()
    req = sample_request()
    result = compute_match_score(ride, req)
    assert result["total_score"] > 90


def test_time_mismatch_lowers_score():
    ride = sample_ride()
    req = sample_request()
    req["ride_time"] = "20:00"
    result = compute_match_score(ride, req)
    assert result["time_compatibility"] == 0.0


def test_seat_unavailable_zero_seat_score():
    ride = sample_ride()
    ride["available_seats"] = 0
    req = sample_request()
    result = compute_match_score(ride, req)
    assert result["seat_availability"] == 0.0


def test_time_compatibility_score_same_time():
    assert time_compatibility_score("2025-09-05", "09:00", "2025-09-05", "09:00") == 1.0


def test_time_compatibility_score_different_date():
    assert time_compatibility_score("2025-09-05", "09:00", "2025-09-06", "09:00") == 0.0


def test_seat_score():
    assert seat_score(3, 1) == 1.0
    assert seat_score(0, 1) == 0.0


def test_rating_score_bounds():
    assert rating_score(5.0) == 1.0
    assert rating_score(0) == 0.0


if __name__ == "__main__":
    test_perfect_match_high_score()
    test_time_mismatch_lowers_score()
    test_seat_unavailable_zero_seat_score()
    test_time_compatibility_score_same_time()
    test_time_compatibility_score_different_date()
    test_seat_score()
    test_rating_score_bounds()
    print("All matching tests passed.")
