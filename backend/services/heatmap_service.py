import pandas as pd
import numpy as np

dataset = pd.read_csv("model/processed_dataset.csv")


def get_heatmap_data(sample_size=1000, severity_filter=None):
    """
    Returns heatmap data with optional severity filtering
    
    Args:
        sample_size: Number of points to return (for performance)
        severity_filter: Optional severity level (0=Fatal, 1=Serious, 2=Slight)
    
    Returns:
        List of dictionaries with lat, lon, severity, and intensity
    """
    
    data_subset = dataset.copy()
    
    # Filter by severity if specified
    if severity_filter is not None:
        data_subset = data_subset[data_subset['Accident_Severity'] == severity_filter]
    
    # If filtered dataset is smaller than sample size, use all
    if len(data_subset) > sample_size:
        data_subset = data_subset.sample(sample_size, random_state=42)
    
    data = []
    for _, row in data_subset.iterrows():
        # Calculate intensity based on severity and casualties
        # 0=Fatal (high intensity), 1=Serious (medium), 2=Slight (low)
        if row['Accident_Severity'] == 0.0:
            intensity = 1.0  # Fatal - maximum intensity
        elif row['Accident_Severity'] == 1.0:
            intensity = 0.7  # Serious
        else:
            intensity = 0.4  # Slight
        
        # Adjust intensity based on casualties
        intensity = min(1.0, intensity * (1 + row['Number_of_Casualties'] * 0.1))
        
        data.append({
            "lat": float(row["latitude"]),
            "lon": float(row["longitude"]),
            "severity": int(row["Accident_Severity"]),
            "severity_label": "Fatal" if row["Accident_Severity"] == 0 else 
                             "Serious" if row["Accident_Severity"] == 1 else "Slight",
            "intensity": float(round(intensity, 2)),
            "casualties": int(row["Number_of_Casualties"]),
            "vehicles": int(row["Number_of_Vehicles"])
        })
    
    return data


def get_clustered_heatmap_data(grid_size=0.05):
    """
    Returns aggregated heatmap data clustered by geographical grid
    Better performance for large datasets
    
    Args:
        grid_size: Size of geographical grid in degrees (default 0.05 ≈ 5.5km)
    
    Returns:
        List of cluster points with aggregated statistics
    """
    
    dataset_copy = dataset.copy()
    
    # Create grid bins
    dataset_copy['lat_bin'] = (dataset_copy['latitude'] / grid_size).astype(int) * grid_size
    dataset_copy['lon_bin'] = (dataset_copy['longitude'] / grid_size).astype(int) * grid_size
    
    # Aggregate by grid
    clustered = dataset_copy.groupby(['lat_bin', 'lon_bin']).agg({
        'Accident_Severity': ['count', 'mean', 'min'],
        'Number_of_Casualties': 'sum',
        'Number_of_Vehicles': 'sum'
    }).reset_index()
    
    clustered.columns = ['lat', 'lon', 'accident_count', 'avg_severity', 
                        'max_severity', 'total_casualties', 'total_vehicles']
    
    data = []
    for _, row in clustered.iterrows():
        # Calculate intensity based on accident count and severity
        base_intensity = min(1.0, row['accident_count'] / 50)  # Normalize by max expected
        severity_factor = (3 - row['avg_severity']) / 3  # Invert: 0=worst, 2=best
        intensity = (base_intensity * 0.6 + severity_factor * 0.4)
        
        data.append({
            "lat": float(row['lat'] + grid_size/2),  # Center of grid
            "lon": float(row['lon'] + grid_size/2),
            "accident_count": int(row['accident_count']),
            "avg_severity": float(round(row['avg_severity'], 2)),
            "total_casualties": int(row['total_casualties']),
            "total_vehicles": int(row['total_vehicles']),
            "intensity": float(round(intensity, 2)),
            "severity_label": "High Risk" if row['avg_severity'] < 1.5 else 
                             "Medium Risk" if row['avg_severity'] < 2.0 else "Low Risk"
        })
    
    # Sort by intensity and return top clusters
    data.sort(key=lambda x: x['intensity'], reverse=True)
    return data[:500]  # Return top 500 clusters