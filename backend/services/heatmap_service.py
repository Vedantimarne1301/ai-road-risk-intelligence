import pandas as pd
import numpy as np

# Load dataset
dataset = pd.read_csv("model/processed_dataset.csv")

# Severity weights: 0=Fatal, 1=Serious, 2=Slight
severity_weights = {0: 3, 1: 2, 2: 1}


def get_heatmap_data(sample_size=1000, severity_filter=None):
    """
    Returns heatmap data with optional severity filtering.
    """
    data_subset = dataset.copy()

    if severity_filter is not None:
        data_subset = data_subset[data_subset['Accident_Severity'] == severity_filter]

    if len(data_subset) > sample_size:
        data_subset = data_subset.sample(sample_size, random_state=42)

    data = []
    for _, row in data_subset.iterrows():
        sev = int(row['Accident_Severity'])
        weight = severity_weights.get(sev, 1)

        # Base intensity by severity
        if sev == 0:
            base_intensity = 1.0
        elif sev == 1:
            base_intensity = 0.7
        else:
            base_intensity = 0.4

        # Weighted by casualties
        intensity = min(1.0, base_intensity * weight * (1 + row['Number_of_Casualties'] * 0.05))

        # Risk label
        if sev == 0:
            risk_label = "High Risk"
        elif sev == 1:
            risk_label = "Medium Risk"
        else:
            risk_label = "Low Risk"

        data.append({
            "lat": float(row["latitude"]),
            "lon": float(row["longitude"]),
            "severity": sev,
            "severity_label": risk_label,
            "intensity": float(round(intensity, 2)),
            "casualties": int(row["Number_of_Casualties"]),
            "vehicles": int(row["Number_of_Vehicles"])
        })

    return data


def get_clustered_heatmap_data(grid_size=0.05):
    """
    Returns aggregated heatmap data clustered by geographical grid
    """
    dataset_copy = dataset.copy()

    # Create grid bins
    dataset_copy['lat_bin'] = (dataset_copy['latitude'] / grid_size).astype(int) * grid_size
    dataset_copy['lon_bin'] = (dataset_copy['longitude'] / grid_size).astype(int) * grid_size

    # Aggregate by grid
    clustered = dataset_copy.groupby(['lat_bin', 'lon_bin']).agg({
        'Accident_Severity': ['count', 'min'],  # count + max severity
        'Number_of_Casualties': 'sum',
        'Number_of_Vehicles': 'sum'
    }).reset_index()

    clustered.columns = ['lat', 'lon', 'accident_count', 'max_severity', 'total_casualties', 'total_vehicles']

    data = []
    for _, row in clustered.iterrows():
        max_sev = int(row['max_severity'])
        high_sev_count = int((dataset_copy[
            (dataset_copy['latitude'] >= row['lat']) &
            (dataset_copy['latitude'] < row['lat'] + grid_size) &
            (dataset_copy['longitude'] >= row['lon']) &
            (dataset_copy['longitude'] < row['lon'] + grid_size)
        ]['Accident_Severity'] <= 1).sum())

        # Base intensity
        severity_factor = (3 - max_sev) / 3  # 0=fatal => highest
        base_intensity = min(1.0, (row['accident_count'] / 50) * 0.6 + severity_factor * 0.4)

        # Risk label
        if max_sev == 0:
            risk_label = "High Risk"
        elif max_sev == 1:
            risk_label = "Medium Risk"
        else:
            risk_label = "Low Risk"

        data.append({
            "lat": float(row['lat'] + grid_size/2),  # center of grid
            "lon": float(row['lon'] + grid_size/2),
            "accident_count": int(row['accident_count']),
            "max_severity": max_sev,
            "high_severity_count": high_sev_count,
            "total_casualties": int(row['total_casualties']),
            "total_vehicles": int(row['total_vehicles']),
            "intensity": float(round(base_intensity, 2)),
            "severity_label": risk_label
        })

    # Sort clusters by intensity descending
    data.sort(key=lambda x: x['intensity'], reverse=True)
    return data[:500]  # return top 500 clusters