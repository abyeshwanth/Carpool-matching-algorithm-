import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.clustering import fit_kmeans, build_zone_clusters, predict_cluster, get_cluster_neighbors


def test_fit_kmeans_basic():
    coords = [(12.9, 77.6), (12.91, 77.61), (13.0, 77.7), (13.01, 77.71)]
    model, labels = fit_kmeans(coords, n_clusters=2)
    assert len(labels) == 4
    assert model.cluster_centers_.shape[0] == 2


def test_build_zone_clusters_from_rides():
    rides = [
        {"id": 1, "source_lat": 12.9, "source_lon": 77.6},
        {"id": 2, "source_lat": 12.91, "source_lon": 77.61},
        {"id": 3, "source_lat": 13.5, "source_lon": 78.0},
    ]
    model, cluster_map = build_zone_clusters(rides, n_clusters=2)
    assert set(cluster_map.keys()) == {1, 2, 3}
    assert cluster_map[1] == cluster_map[2]  # close points, same cluster


def test_predict_cluster():
    coords = [(12.9, 77.6), (13.5, 78.0)]
    model, _ = fit_kmeans(coords, n_clusters=2)
    c = predict_cluster(model, 12.9, 77.6)
    assert isinstance(c, int)


def test_empty_rides_returns_none():
    model, cluster_map = build_zone_clusters([], n_clusters=3)
    assert model is None
    assert cluster_map == {}


if __name__ == "__main__":
    test_fit_kmeans_basic()
    test_build_zone_clusters_from_rides()
    test_predict_cluster()
    test_empty_rides_returns_none()
    print("All clustering tests passed.")
