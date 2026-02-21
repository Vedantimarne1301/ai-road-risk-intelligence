import pandas as pd
import numpy as np
import joblib
from scipy.spatial import cKDTree
from services.predict import predict_pipeline

# Load dataset and features
DATA_PATH = "model/processed_dataset.csv"
FEATURES_PATH = "model/model_features.pkl"

dataset = pd.read_csv(DATA_PATH)
feature_columns = joblib.load(FEATURES_PATH)

# KD-Tree for fast spatial queries
coords = dataset[['latitude', 'longitude']].values
kdtree = cKDTree(coords)

# Map string risk to numeric for frontend
RISK_TO_SEV = {"High": 0, "Medium": 1, "Low": 2}


def find_nearest_accidents(lat, lon, k=50):
    distances, indices = kdtree.query([lat, lon], k=k)
    nearest = dataset.iloc[indices].copy()
    nearest['distance_km'] = distances * 111  # Approx degrees → km
    return nearest


def aggregate_location_features(lat, lon, radius_km=5.0):
    """
    Aggregate features from nearby accidents using distance weighting.
    """
    nearby = find_nearest_accidents(lat, lon, k=50)
    in_radius = nearby[nearby['distance_km'] <= radius_km]

    # Fallback if no accidents in radius
    if len(in_radius) == 0:
        in_radius = nearby.head(10)

    feature_dict = {}
    weights = 1 / (in_radius['distance_km'] + 0.1)  # closer accidents matter more

    for col in feature_columns:
        if col == 'latitude':
            feature_dict[col] = lat
        elif col == 'longitude':
            feature_dict[col] = lon
        elif col in in_radius.columns:
            if pd.api.types.is_numeric_dtype(in_radius[col]):
                feature_dict[col] = np.average(in_radius[col], weights=weights)
            else:
                mode_val = in_radius[col].mode()
                feature_dict[col] = mode_val[0] if len(mode_val) > 0 else np.nan
        else:
            feature_dict[col] = np.nan

    # Contextual features
    feature_dict['accident_count_radius'] = len(in_radius)
    feature_dict['avg_severity_radius'] = float(in_radius['Accident_Severity'].mean())
    feature_dict['nearest_accident_km'] = float(in_radius['distance_km'].min())

    return feature_dict


def get_features_from_location(lat, lon, use_aggregation=True):
    if use_aggregation:
        return aggregate_location_features(lat, lon)
    else:
        nearest = find_nearest_accidents(lat, lon, k=1).iloc[0]
        feature_dict = {col: nearest.get(col, np.nan) for col in feature_columns}
        feature_dict['latitude'] = lat
        feature_dict['longitude'] = lon
        feature_dict['accident_count_radius'] = 1
        feature_dict['avg_severity_radius'] = float(nearest['Accident_Severity'])
        feature_dict['nearest_accident_km'] = 0.0
        return feature_dict


def predict_risk_for_location(lat, lon):
    """
    Predict risk for a location.
    """
    features = get_features_from_location(lat, lon, use_aggregation=True)
    prediction = predict_pipeline(features)
    prediction['severity'] = RISK_TO_SEV[prediction['risk_level']]
    return prediction