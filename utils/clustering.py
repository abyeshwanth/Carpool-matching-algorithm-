"""
clustering.py - K-Means clustering module.

Groups rides and ride requests into geographic "zones" based on their
source coordinates. This narrows the matching search space: instead of
comparing a new request against every active ride in the city, we first
find rides in the same (or an adjacent) cluster, then run the fine-grained
matching-score algorithm only within that neighborhood.
"""

import numpy as np
from sklearn.cluster import KMeans
import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "kmeans_model.pkl")


def fit_kmeans(coords, n_clusters=5, random_state=42):
    """
    Fit a K-Means model on a list of (lat, lon) coordinates.
    Returns the fitted model and the cluster label for each point.
    """
    coords = np.array(coords)
    n_clusters = min(n_clusters, len(coords)) if len(coords) > 0 else 1
    n_clusters = max(n_clusters, 1)

    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = model.fit_predict(coords)
    return model, labels


def save_model(model):
    joblib.dump(model, MODEL_PATH)


def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None


def predict_cluster(model, lat, lon):
    """Predict which cluster a single (lat, lon) point belongs to."""
    if model is None:
        return 0
    return int(model.predict(np.array([[lat, lon]]))[0])


def build_zone_clusters(rides, n_clusters=5):
    """
    Given a list of ride dicts (each with source_lat/source_lon), fit a
    K-Means model on their source coordinates and return:
      - the fitted model
      - a dict mapping ride_id -> cluster_id
    """
    if not rides:
        return None, {}

    coords = [(r["source_lat"], r["source_lon"]) for r in rides]
    model, labels = fit_kmeans(coords, n_clusters=n_clusters)

    ride_cluster_map = {rides[i]["id"]: int(labels[i]) for i in range(len(rides))}
    save_model(model)
    return model, ride_cluster_map


def get_cluster_neighbors(model, lat, lon, all_labels, top_k=2):
    """
    Find the nearest `top_k` cluster centers to a given point, so we can
    also search "nearby" zones and not just the exact cluster.
    Returns a list of cluster ids.
    """
    if model is None:
        return [0]
    centers = model.cluster_centers_
    point = np.array([lat, lon])
    dists = np.linalg.norm(centers - point, axis=1)
    nearest = np.argsort(dists)[:top_k]
    return [int(c) for c in nearest]
