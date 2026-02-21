import pandas as pd
import numpy as np
import joblib
from scipy.spatial import cKDTree

# Load processed dataset
DATA_PATH = "model/processed_dataset.csv"
dataset = pd.read_csv(DATA_PATH)

# Load feature columns
feature_columns = joblib.load("model/model_features.pkl")

# Build KD-Tree for fast spatial lookups
coords = dataset[['latitude', 'longitude']].values
kdtree = cKDTree(coords)


def find_nearest_accidents(lat, lon, k=50, radius_km=None):
    """
    Finds nearest accidents to a location, optionally filtered by radius.
    """
    distances, indices = kdtree.query([lat, lon], k=k)
    nearest_accidents = dataset.iloc[indices].copy()
    nearest_accidents['distance_km'] = distances * 111  # approximate conversion

    if radius_km:
        filtered = nearest_accidents[nearest_accidents['distance_km'] <= radius_km]
        if len(filtered) > 0:
            nearest_accidents = filtered

    return nearest_accidents


def aggregate_location_features(lat, lon, initial_radius_km=5.0, max_radius_km=15.0):
    """
    Aggregate features from nearby accidents with distance weighting.
    Automatically increases radius for sparse areas.
    """
    radius = initial_radius_km
    nearby = find_nearest_accidents(lat, lon, k=50, radius_km=radius)

    # Expand radius if too few accidents are nearby
    while len(nearby) < 5 and radius <= max_radius_km:
        radius += 5
        nearby = find_nearest_accidents(lat, lon, k=50, radius_km=radius)
    
    if len(nearby) == 0:
        # Extreme fallback: take the single nearest accident
        nearby = find_nearest_accidents(lat, lon, k=1)

    # Weight closer accidents more
    nearby['weight'] = 1 / (nearby['distance_km'] + 0.1)

    feature_dict = {}

    for col in feature_columns:
        if col in ['latitude', 'longitude']:
            feature_dict[col] = lat if col == 'latitude' else lon
        elif col in nearby.columns:
            if pd.api.types.is_numeric_dtype(nearby[col]):
                # Weighted average instead of median
                feature_dict[col] = np.average(nearby[col], weights=nearby['weight'])
            else:
                # Use mode for categorical
                mode_val = nearby[col].mode()
                feature_dict[col] = mode_val[0] if len(mode_val) > 0 else np.nan
        else:
            feature_dict[col] = np.nan

    # Add accident density as a feature
    feature_dict['accident_density'] = len(nearby) / (np.pi * radius**2)

    return feature_dict


def get_features_from_location(lat, lon, use_aggregation=True):
    """
    Converts map location into model-ready feature dictionary.
    """
    if use_aggregation:
        return aggregate_location_features(lat, lon)
    else:
        nearest = find_nearest_accidents(lat, lon, k=1).iloc[0]
        feature_dict = {}
        for col in feature_columns:
            feature_dict[col] = nearest[col] if col in nearest else np.nan
        feature_dict['latitude'] = lat
        feature_dict['longitude'] = lon
        feature_dict['accident_density'] = 0
        return feature_dict


def get_location_context(lat, lon, radius_km=10.0):
    """
    Get contextual information about a location for UI display.
    """
    nearby = find_nearest_accidents(lat, lon, k=100)
    nearby['distance_km'] = nearby['distance'] * 111
    in_radius = nearby[nearby['distance_km'] <= radius_km]

    if len(in_radius) == 0:
        return {
            "accident_count": 0,
            "radius_km": radius_km,
            "message": f"No accidents found within {radius_km}km"
        }

    return {
        "accident_count": len(in_radius),
        "radius_km": radius_km,
        "severity_distribution": {
            "fatal": int((in_radius['Accident_Severity'] == 0).sum()),
            "serious": int((in_radius['Accident_Severity'] == 1).sum()),
            "slight": int((in_radius['Accident_Severity'] == 2).sum())
        },
        "avg_severity": float(in_radius['Accident_Severity'].mean()),
        "nearest_accident_km": float(nearby.iloc[0]['distance_km'])
    }