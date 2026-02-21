import pandas as pd
import numpy as np
import joblib
from scipy.spatial import cKDTree

# Load processed dataset
DATA_PATH = "model/processed_dataset.csv"
dataset = pd.read_csv(DATA_PATH)

# Load model features
feature_columns = joblib.load("model/model_features.pkl")

# Build KD-Tree for fast spatial lookup
coords = dataset[['latitude', 'longitude']].values
kdtree = cKDTree(coords)

# Severity weight mapping: 0=Fatal, 1=Serious, 2=Slight
severity_weights = {0: 3, 1: 2, 2: 1}


def find_nearest_accidents(lat, lon, k=50):
    """
    Find K nearest accidents
    """
    distances, indices = kdtree.query([lat, lon], k=k)
    nearest_accidents = dataset.iloc[indices].copy()
    nearest_accidents['distance'] = distances
    return nearest_accidents


def aggregate_location_features(lat, lon, radius_km=10.0):
    """
    Aggregate features with:
    - Weighted max for numeric features (preserve extreme risk)
    - Hotspot indicators (max severity, high severity counts)
    - Distance weighting to emphasize nearby serious accidents
    """
    nearby = find_nearest_accidents(lat, lon, k=100)
    nearby['distance_km'] = nearby['distance'] * 111

    # Accidents within radius
    in_radius = nearby[nearby['distance_km'] <= radius_km]

    # Fallback to closest accidents if none
    if len(in_radius) == 0:
        in_radius = nearby.head(10)

    feature_dict = {}

    # Weighted aggregation for numeric features
    for col in feature_columns:
        if col in ['latitude', 'longitude']:
            feature_dict[col] = lat if col == 'latitude' else lon
        elif col in in_radius.columns:
            if pd.api.types.is_numeric_dtype(in_radius[col]):
                # Weighted max: preserve extreme values
                weighted_values = []
                for _, row in in_radius.iterrows():
                    weight = severity_weights.get(row['Accident_Severity'], 1)
                    dist_factor = 1 + row['distance_km'] / 10
                    weighted_values.append(row[col] * weight / dist_factor)
                feature_dict[col] = max(weighted_values)
            else:
                # Use most risky category (associated with max severity)
                idx_max_sev = in_radius['Accident_Severity'].idxmin()  # 0=Fatal, 1=Serious
                feature_dict[col] = in_radius.loc[idx_max_sev, col]
        else:
            feature_dict[col] = np.nan

    # Hotspot / risk indicators
    feature_dict['max_severity_radius'] = int(in_radius['Accident_Severity'].min())  # 0=Fatal
    feature_dict['high_severity_count'] = int((in_radius['Accident_Severity'] <= 1).sum())
    feature_dict['nearest_high_severity_km'] = float(
        in_radius[in_radius['Accident_Severity'] <= 1]['distance_km'].min()
        if len(in_radius[in_radius['Accident_Severity'] <= 1]) > 0 else radius_km
    )
    feature_dict['accident_count_radius'] = len(in_radius)
    feature_dict['avg_severity_radius'] = float(in_radius['Accident_Severity'].mean())
    feature_dict['nearest_accident_km'] = float(in_radius['distance_km'].min())

    return feature_dict


def get_features_from_location(lat, lon, use_aggregation=True):
    """
    Converts map location into model-ready features.
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
        feature_dict['max_severity_radius'] = int(nearest['Accident_Severity'])
        feature_dict['high_severity_count'] = 1 if nearest['Accident_Severity'] <= 1 else 0
        feature_dict['nearest_high_severity_km'] = 0.0
        feature_dict['accident_count_radius'] = 1
        feature_dict['avg_severity_radius'] = float(nearest['Accident_Severity'])
        feature_dict['nearest_accident_km'] = 0.0
        return feature_dict


def get_location_context(lat, lon, radius_km=10.0):
    """
    Provides context for map display
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
        "nearest_accident_km": float(nearby.iloc[0]['distance_km']),
        "max_severity_radius": int(in_radius['Accident_Severity'].min()),
        "high_severity_count": int((in_radius['Accident_Severity'] <= 1).sum()),
        "nearest_high_severity_km": float(
            in_radius[in_radius['Accident_Severity'] <= 1]['distance_km'].min()
            if len(in_radius[in_radius['Accident_Severity'] <= 1]) > 0 else radius_km
        )
    }