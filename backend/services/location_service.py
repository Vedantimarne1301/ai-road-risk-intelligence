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


def find_nearest_accidents(lat, lon, k=50):
    """
    Find K nearest accidents to provide better statistical representation.
    """
    distances, indices = kdtree.query([lat, lon], k=k)
    nearest_accidents = dataset.iloc[indices].copy()
    nearest_accidents['distance'] = distances
    return nearest_accidents


def aggregate_location_features(lat, lon, radius_km=10.0):
    """
    Aggregate features from nearby accidents with weighted influence by distance.
    Includes accident density, average severity, and nearest accident distance.
    """
    nearby = find_nearest_accidents(lat, lon, k=50)
    nearby['distance_km'] = nearby['distance'] * 111  # approx conversion

    # Filter by radius
    in_radius = nearby[nearby['distance_km'] <= radius_km]

    if len(in_radius) == 0:
        # fallback: take 10 closest accidents
        in_radius = nearby.head(10)

    feature_dict = {}

    # Weighted aggregation for numeric features
    weights = 1 / (in_radius['distance_km'] + 0.1)  # avoid divide by zero

    for col in feature_columns:
        if col in ['latitude', 'longitude']:
            feature_dict[col] = lat if col == 'latitude' else lon
        elif col in in_radius.columns:
            if pd.api.types.is_numeric_dtype(in_radius[col]):
                feature_dict[col] = np.average(in_radius[col], weights=weights)
            else:
                mode_val = in_radius[col].mode()
                feature_dict[col] = mode_val[0] if len(mode_val) > 0 else np.nan
        else:
            feature_dict[col] = np.nan

    # Add contextual features
    feature_dict['accident_count_radius'] = len(in_radius)
    feature_dict['avg_severity_radius'] = float(in_radius['Accident_Severity'].mean())
    feature_dict['nearest_accident_km'] = float(in_radius['distance_km'].min())

    return feature_dict


def get_features_from_location(lat, lon, use_aggregation=True):
    """
    Converts map location into model-ready feature dictionary.
    """
    if use_aggregation:
        return aggregate_location_features(lat, lon, radius_km=10.0)
    else:
        nearest = find_nearest_accidents(lat, lon, k=1).iloc[0]
        feature_dict = {}
        for col in feature_columns:
            feature_dict[col] = nearest.get(col, np.nan)
        feature_dict['latitude'] = lat
        feature_dict['longitude'] = lon
        feature_dict['accident_count_radius'] = 1
        feature_dict['avg_severity_radius'] = float(nearest['Accident_Severity'])
        feature_dict['nearest_accident_km'] = 0.0
        return feature_dict


def get_location_context(lat, lon, radius_km=10.0):
    """
    Provides location context for display: accident count, severity distribution, nearest accident.
    """
    nearby = find_nearest_accidents(lat, lon, k=100)
    nearby['distance_km'] = nearby['distance'] * 111
    in_radius = nearby[nearby['distance_km'] <= radius_km]

    if len(in_radius) == 0:
        return {
            "accident_count": 0,
            "radius_km": radius_km,
            "message": f"No accidents found within {radius_km} km"
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