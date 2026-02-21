import pandas as pd
import numpy as np
from collections import Counter

# Load the processed dataset
DATA_PATH = "model//processed_dataset.csv"
dataset = pd.read_csv(DATA_PATH)


# ---------------------------------------------------
# Mapping Dictionaries for Better Readability
# ---------------------------------------------------
SEVERITY_MAP = {
    0.0: "Fatal",
    1.0: "Serious", 
    2.0: "Slight"
}

LIGHT_CONDITIONS_MAP = {
    1.0: "Daylight",
    4.0: "Darkness - lights lit",
    5.0: "Darkness - lights unlit",
    6.0: "Darkness - no lighting",
    7.0: "Darkness - lighting unknown"
}

WEATHER_CONDITIONS_MAP = {
    1.0: "Fine no high winds",
    2.0: "Raining no high winds",
    3.0: "Snowing no high winds",
    4.0: "Fine + high winds",
    5.0: "Raining + high winds",
    6.0: "Snowing + high winds",
    7.0: "Fog or mist",
    8.0: "Other",
    9.0: "Unknown"
}

ROAD_SURFACE_MAP = {
    1.0: "Dry",
    2.0: "Wet or damp",
    3.0: "Snow",
    4.0: "Frost or ice",
    5.0: "Flood over 3cm deep",
    6.0: "Oil or diesel",
    7.0: "Mud"
}

DAY_OF_WEEK_MAP = {
    1.0: "Sunday",
    2.0: "Monday",
    3.0: "Tuesday",
    4.0: "Wednesday",
    5.0: "Thursday",
    6.0: "Friday",
    7.0: "Saturday"
}


# ---------------------------------------------------
# Dashboard Statistics
# ---------------------------------------------------
def get_dashboard_statistics():
    """
    Returns overall statistics about accidents in the dataset
    """
    
    total_accidents = len(dataset)
    
    # Severity distribution (0=Fatal, 1=Serious, 2=Slight)
    severity_counts = dataset['Accident_Severity'].value_counts().to_dict()
    severity_distribution = {
        "fatal": int(severity_counts.get(0.0, 0)),
        "serious": int(severity_counts.get(1.0, 0)),
        "slight": int(severity_counts.get(2.0, 0))
    }
    
    # High risk locations (Fatal + Serious accidents)
    high_risk_count = int((dataset['Accident_Severity'] <= 1.0).sum())
    
    # Total casualties
    total_casualties = int(dataset['Number_of_Casualties'].sum())
    
    # Average vehicles per accident
    avg_vehicles = int(dataset['Number_of_Vehicles'].mean())
    
    # Most dangerous hour
    dangerous_hour = int(dataset.groupby('Hour')['Accident_Severity'].apply(
        lambda x: (x <= 1.0).sum()
    ).idxmax())
    
    # Most dangerous day
    dangerous_day_num = int(dataset.groupby('Day_of_Week')['Accident_Severity'].apply(
        lambda x: (x <= 1.0).sum()
    ).idxmax())
    dangerous_day = DAY_OF_WEEK_MAP.get(dangerous_day_num, "Unknown")
    
    return {
        "total_accidents": total_accidents,
        "total_casualties": total_casualties,
        "high_risk_locations": high_risk_count,
        "severity_distribution": severity_distribution,
        "avg_vehicles_per_accident": round(avg_vehicles, 2),
        "most_dangerous_hour": dangerous_hour,
        "most_dangerous_day": dangerous_day,
        "date_range": {
            "months_covered": "12 months",
            "description": "Comprehensive accident data analysis"
        }
    }


# ---------------------------------------------------
# Risk Factors Distribution
# ---------------------------------------------------
def get_risk_factors_distribution():
    """
    Returns distribution of top contributing factors
    """
    
    factors = {}
    
    # Weather conditions distribution (top 5)
    weather_counts = dataset['Weather_Conditions'].value_counts().head(5)
    factors['weather_conditions'] = [
        {
            "condition": WEATHER_CONDITIONS_MAP.get(float(k), f"Code {int(k)}"),
            "count": int(v),
            "percentage": round((v / len(dataset)) * 100, 2)
        }
        for k, v in weather_counts.items()
    ]
    
    # Light conditions distribution (top 5)
    light_counts = dataset['Light_Conditions'].value_counts().head(5)
    factors['light_conditions'] = [
        {
            "condition": LIGHT_CONDITIONS_MAP.get(float(k), f"Code {int(k)}"),
            "count": int(v),
            "percentage": round((v / len(dataset)) * 100, 2)
        }
        for k, v in light_counts.items()
    ]
    
    # Road surface conditions (top 5)
    road_counts = dataset['Road_Surface_Conditions'].value_counts().head(5)
    factors['road_surface_conditions'] = [
        {
            "condition": ROAD_SURFACE_MAP.get(float(k), f"Code {int(k)}"),
            "count": int(v),
            "percentage": round((v / len(dataset)) * 100, 2)
        }
        for k, v in road_counts.items()
    ]
    
    # Speed limit distribution
    speed_counts = dataset['Speed_limit'].value_counts().head(5)
    factors['speed_limits'] = [
        {
            "speed": int(k),
            "count": int(v),
            "percentage": round((v / len(dataset)) * 100, 2)
        }
        for k, v in speed_counts.items()
    ]
    
    # Urban vs Rural
    urban_rural_counts = dataset['Urban_or_Rural_Area'].value_counts()
    factors['urban_rural'] = [
        {
            "area": "Urban" if k == 1.0 else "Rural",
            "count": int(v),
            "percentage": round((v / len(dataset)) * 100, 2)
        }
        for k, v in urban_rural_counts.items()
    ]
    
    return factors


# ---------------------------------------------------
# Top Risky Locations
# ---------------------------------------------------
def get_top_risky_locations(limit=10):
    """
    Returns top locations with highest accident frequency and severity
    """
    
    # Round coordinates to reduce granularity (cluster nearby accidents)
    dataset_copy = dataset.copy()
    dataset_copy['lat_rounded'] = dataset_copy['latitude'].round(3)
    dataset_copy['lon_rounded'] = dataset_copy['longitude'].round(3)
    
    # Group by rounded location
    location_groups = dataset_copy.groupby(['lat_rounded', 'lon_rounded']).agg({
        'Accident_Severity': ['count', 'mean'],
        'Number_of_Casualties': 'sum'
    }).reset_index()
    
    location_groups.columns = ['lat', 'lon', 'accident_count', 'avg_severity', 'total_casualties']
    
    # Calculate risk score (lower severity number = more severe)
    # 0=Fatal, 1=Serious, 2=Slight, so we invert it
    location_groups['risk_score'] = (
        (location_groups['accident_count'] * 0.4) + 
        ((3 - location_groups['avg_severity']) * 10) +  # Invert severity
        (location_groups['total_casualties'] * 0.3)
    )
    
    # Sort by risk score
    top_locations = location_groups.nlargest(limit, 'risk_score')
    
    result = []
    for idx, row in top_locations.iterrows():
        # Determine risk level based on severity
        if row['avg_severity'] <= 0.5:
            risk_level = "Critical"
        elif row['avg_severity'] <= 1.2:
            risk_level = "High"
        else:
            risk_level = "Medium"
            
        result.append({
            "rank": len(result) + 1,
            "lat": float(row['lat']),
            "lon": float(row['lon']),
            "accident_count": int(row['accident_count']),
            "avg_severity": float(round(row['avg_severity'], 2)),
            "total_casualties": int(row['total_casualties']),
            "risk_score": float(round(row['risk_score'], 2)),
            "risk_level": risk_level
        })
    
    return result


# ---------------------------------------------------
# Severity Analysis by Conditions
# ---------------------------------------------------
def get_severity_by_conditions():
    """
    Returns severity breakdown by different conditions
    """
    
    result = {}
    
    # Severity by Speed Limit
    speed_severity = dataset.groupby('Speed_limit').agg({
        'Accident_Severity': ['mean', 'count']
    }).reset_index()
    speed_severity.columns = ['speed_limit', 'avg_severity', 'count']
    speed_severity = speed_severity[speed_severity['count'] >= 10]  # Filter low counts
    
    result['by_speed_limit'] = [
        {
            "speed": int(row['speed_limit']),
            "avg_severity": float(round(row['avg_severity'], 2)),
            "accident_count": int(row['count'])
        }
        for _, row in speed_severity.sort_values('speed_limit').iterrows()
    ]
    
    # Severity by Hour of Day
    hourly_severity = dataset.groupby('Hour').agg({
        'Accident_Severity': ['mean', 'count']
    }).reset_index()
    hourly_severity.columns = ['hour', 'avg_severity', 'count']
    
    result['by_hour'] = [
        {
            "hour": int(row['hour']),
            "avg_severity": float(round(row['avg_severity'], 2)),
            "accident_count": int(row['count'])
        }
        for _, row in hourly_severity.sort_values('hour').iterrows()
    ]
    
    # Severity by Day of Week
    daily_severity = dataset.groupby('Day_of_Week').agg({
        'Accident_Severity': ['mean', 'count']
    }).reset_index()
    daily_severity.columns = ['day', 'avg_severity', 'count']
    
    result['by_day_of_week'] = [
        {
            "day": DAY_OF_WEEK_MAP.get(row['day'], "Unknown"),
            "avg_severity": float(round(row['avg_severity'], 2)),
            "accident_count": int(row['count'])
        }
        for _, row in daily_severity.sort_values('day').iterrows()
    ]
    
    # Severity by Weather
    weather_severity = dataset.groupby('Weather_Conditions').agg({
        'Accident_Severity': ['mean', 'count']
    }).reset_index()
    weather_severity.columns = ['weather', 'avg_severity', 'count']
    weather_severity = weather_severity[weather_severity['count'] >= 50]
    
    result['by_weather'] = [
        {
            "weather": WEATHER_CONDITIONS_MAP.get(row['weather'], f"Code {int(row['weather'])}"),
            "avg_severity": float(round(row['avg_severity'], 2)),
            "accident_count": int(row['count'])
        }
        for _, row in weather_severity.sort_values('avg_severity').iterrows()
    ]
    
    # Severity by Number of Vehicles
    vehicle_severity = dataset.groupby('Number_of_Vehicles').agg({
        'Accident_Severity': ['mean', 'count']
    }).reset_index()
    vehicle_severity.columns = ['vehicles', 'avg_severity', 'count']
    vehicle_severity = vehicle_severity[vehicle_severity['vehicles'] <= 5]
    
    result['by_vehicle_count'] = [
        {
            "vehicle_count": int(row['vehicles']),
            "avg_severity": float(round(row['avg_severity'], 2)),
            "accident_count": int(row['count'])
        }
        for _, row in vehicle_severity.sort_values('vehicles').iterrows()
    ]
    
    return result


# ---------------------------------------------------
# Geographical Distribution
# ---------------------------------------------------
def get_geographical_distribution():
    """
    Returns accidents grouped by geographical regions (grid-based)
    """
    
    # Create geographical grid (0.1 degree bins ≈ 11km)
    dataset_copy = dataset.copy()
    dataset_copy['lat_bin'] = (dataset_copy['latitude'] / 0.1).astype(int) * 0.1
    dataset_copy['lon_bin'] = (dataset_copy['longitude'] / 0.1).astype(int) * 0.1
    
    geo_distribution = dataset_copy.groupby(['lat_bin', 'lon_bin']).agg({
        'Accident_Severity': ['count', 'mean']
    }).reset_index()
    
    geo_distribution.columns = ['lat', 'lon', 'accident_count', 'avg_severity']
    
    # Filter out low-count areas
    geo_distribution = geo_distribution[geo_distribution['accident_count'] >= 5]
    
    # Sort by accident count and take top 30
    geo_distribution = geo_distribution.nlargest(30, 'accident_count')
    
    result = []
    for _, row in geo_distribution.iterrows():
        result.append({
            "lat": float(row['lat'] + 0.05),  # Center of bin
            "lon": float(row['lon'] + 0.05),
            "accident_count": int(row['accident_count']),
            "avg_severity": float(round(row['avg_severity'], 2))
        })
    
    return result


# ---------------------------------------------------
# Time-based Trends
# ---------------------------------------------------
def get_time_trends():
    """
    Returns accident trends by time (hourly, daily, monthly)
    """
    
    # Monthly distribution
    monthly = dataset.groupby('Month').agg({
        'Accident_Severity': ['count', 'mean']
    }).reset_index()
    monthly.columns = ['month', 'count', 'avg_severity']
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    monthly_data = [
        {
            "month": month_names[int(row['month'])-1],
            "accident_count": int(row['count']),
            "avg_severity": float(round(row['avg_severity'], 2))
        }
        for _, row in monthly.sort_values('month').iterrows()
    ]
    
    # Hourly distribution
    hourly = dataset.groupby('Hour').size().reset_index(name='count')
    hourly_data = [
        {
            "hour": int(row['Hour']),
            "accident_count": int(row['count'])
        }
        for _, row in hourly.sort_values('Hour').iterrows()
    ]
    
    # Day of week distribution
    daily = dataset.groupby('Day_of_Week').size().reset_index(name='count')
    daily_data = [
        {
            "day": DAY_OF_WEEK_MAP.get(row['Day_of_Week'], "Unknown"),
            "accident_count": int(row['count'])
        }
        for _, row in daily.sort_values('Day_of_Week').iterrows()
    ]
    
    return {
        "monthly": monthly_data,
        "hourly": hourly_data,
        "daily": daily_data
    }