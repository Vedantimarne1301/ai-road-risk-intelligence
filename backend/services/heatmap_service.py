import pandas as pd
from services.location_service import get_features_from_location
from services.predict import predict_pipeline

# Load dataset
dataset = pd.read_csv("model/processed_dataset.csv")

# Map string risk to numeric for frontend
RISK_TO_SEV = {"High": 0, "Medium": 1, "Low": 2}


def get_heatmap_data(sample_size=1000, radius_km=5.0):
    """
    Returns heatmap points with model-aligned risk, compatible with frontend.
    """
    # Sample dataset for performance
    if len(dataset) > sample_size:
        data_subset = dataset.sample(sample_size, random_state=42)
    else:
        data_subset = dataset.copy()

    heatmap_points = []
    for _, row in data_subset.iterrows():
        lat = float(row["latitude"])
        lon = float(row["longitude"])

        # Get features for prediction
        features = get_features_from_location(lat, lon, use_aggregation=True)
        prediction = predict_pipeline(features)
        risk_level = prediction["risk_level"]
        risk_score = prediction["risk_score"]

        # Numeric severity for frontend mapping
        severity = RISK_TO_SEV[risk_level]

        # Intensity for visualization
        intensity = {"High": 1.0, "Medium": 0.7, "Low": 0.4}[risk_level]

        heatmap_points.append({
            "lat": lat,
            "lon": lon,
            "severity": severity,        # numeric for frontend
            "risk_level": risk_level,    # string
            "risk_score": float(risk_score),
            "intensity": float(intensity),
            "top_factors": prediction["top_factors"],
            "casualties": int(row.get("Number_of_Casualties", 0)),
            "vehicles": int(row.get("Number_of_Vehicles", 0))
        })

    return heatmap_points


def get_clustered_heatmap_data(grid_size=0.05, radius_km=5.0):
    """
    Returns aggregated heatmap clusters with model-aligned risk.
    """
    dataset_copy = dataset.copy()

    # Create grid bins
    dataset_copy['lat_bin'] = (dataset_copy['latitude'] / grid_size).astype(int) * grid_size
    dataset_copy['lon_bin'] = (dataset_copy['longitude'] / grid_size).astype(int) * grid_size

    clustered_points = []
    grouped = dataset_copy.groupby(['lat_bin', 'lon_bin'])

    for (lat_bin, lon_bin), group in grouped:
        # Center of grid
        lat_center = lat_bin + grid_size / 2
        lon_center = lon_bin + grid_size / 2

        # Get features & prediction for center
        features = get_features_from_location(lat_center, lon_center, use_aggregation=True)
        prediction = predict_pipeline(features)
        risk_level = prediction["risk_level"]
        risk_score = prediction["risk_score"]
        severity = RISK_TO_SEV[risk_level]

        intensity = {"High": 1.0, "Medium": 0.7, "Low": 0.4}[risk_level]

        clustered_points.append({
            "lat": lat_center,
            "lon": lon_center,
            "severity": severity,        # numeric for frontend
            "risk_level": risk_level,
            "risk_score": float(risk_score),
            "intensity": float(intensity),
            "top_factors": prediction["top_factors"],
            "accident_count": len(group),
            "total_casualties": int(group["Number_of_Casualties"].sum()),
            "total_vehicles": int(group["Number_of_Vehicles"].sum())
        })

    # Sort by intensity descending
    clustered_points.sort(key=lambda x: x['intensity'], reverse=True)
    return clustered_points[:500]  # top 500 clusters