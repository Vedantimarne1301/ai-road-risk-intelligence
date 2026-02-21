import pandas as pd
from services.location_service import predict_risk_for_location

# Load dataset
DATA_PATH = "model/processed_dataset.csv"
dataset = pd.read_csv(DATA_PATH)

# Map string risk to numeric for frontend
RISK_TO_SEV = {"High": 0, "Medium": 1, "Low": 2}

# Intensity for map visualization
INTENSITY_MAP = {"High": 1.0, "Medium": 0.7, "Low": 0.4}


def get_heatmap_data(sample_size=1000):
    """
    Returns model-aligned heatmap points.
    """
    if len(dataset) > sample_size:
        data_subset = dataset.sample(sample_size, random_state=42)
    else:
        data_subset = dataset.copy()

    heatmap_points = []
    for _, row in data_subset.iterrows():
        lat = float(row["latitude"])
        lon = float(row["longitude"])
        prediction = predict_risk_for_location(lat, lon)
        risk_level = prediction["risk_level"]

        heatmap_points.append({
            "lat": lat,
            "lon": lon,
            "severity": RISK_TO_SEV[risk_level],
            "risk_level": risk_level,
            "risk_score": float(prediction["risk_score"]),
            "intensity": float(INTENSITY_MAP[risk_level]),
            "top_factors": prediction["top_factors"],
            "casualties": int(row.get("Number_of_Casualties", 0)),
            "vehicles": int(row.get("Number_of_Vehicles", 0))
        })

    return heatmap_points


def get_clustered_heatmap_data(grid_size=0.05):
    """
    Returns aggregated heatmap clusters (centered grid points).
    """
    dataset_copy = dataset.copy()
    dataset_copy['lat_bin'] = (dataset_copy['latitude'] / grid_size).astype(int) * grid_size
    dataset_copy['lon_bin'] = (dataset_copy['longitude'] / grid_size).astype(int) * grid_size

    clustered_points = []
    grouped = dataset_copy.groupby(['lat_bin', 'lon_bin'])

    for (lat_bin, lon_bin), group in grouped:
        lat_center = lat_bin + grid_size / 2
        lon_center = lon_bin + grid_size / 2
        prediction = predict_risk_for_location(lat_center, lon_center)
        risk_level = prediction["risk_level"]

        clustered_points.append({
            "lat": lat_center,
            "lon": lon_center,
            "severity": RISK_TO_SEV[risk_level],
            "risk_level": risk_level,
            "risk_score": float(prediction["risk_score"]),
            "intensity": float(INTENSITY_MAP[risk_level]),
            "top_factors": prediction["top_factors"],
            "accident_count": len(group),
            "total_casualties": int(group["Number_of_Casualties"].sum()),
            "total_vehicles": int(group["Number_of_Vehicles"].sum())
        })

    # Sort clusters by intensity descending
    clustered_points.sort(key=lambda x: x['intensity'], reverse=True)
    return clustered_points[:500]