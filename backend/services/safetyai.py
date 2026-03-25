"""
Safety AI Chatbot Service - FINAL WORKING VERSION
Natural language interface with structured fallback responses
"""

import pandas as pd
import numpy as np
from langchain_groq import ChatGroq
import os
import json
import re
from typing import Dict, List, Any, Optional

# Load dataset
DATA_PATH = "model/processed_dataset.csv"
dataset = pd.read_csv(DATA_PATH)

# Initialize LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.3,
    max_tokens=2000
)


# ============================================================
# DATA ANALYSIS FUNCTIONS
# ============================================================

def get_severity_distribution() -> Dict[str, Any]:
    """Get accident severity distribution"""
    severity_counts = dataset['Accident_Severity'].value_counts().to_dict()
    total = len(dataset)
    
    return {
        "total_accidents": total,
        "fatal": int(severity_counts.get(0, 0)),
        "serious": int(severity_counts.get(1, 0)),
        "slight": int(severity_counts.get(2, 0)),
        "fatal_pct": round(severity_counts.get(0, 0) / total * 100, 2),
        "serious_pct": round(severity_counts.get(1, 0) / total * 100, 2),
        "slight_pct": round(severity_counts.get(2, 0) / total * 100, 2)
    }


def get_time_patterns() -> Dict[str, Any]:
    """Analyze accident patterns by time"""
    if 'Hour' not in dataset.columns:
        return {"error": "Time data not available"}
    
    hour_counts = dataset.groupby('Hour').size().to_dict()
    peak_hour = max(hour_counts.items(), key=lambda x: x[1])
    
    if 'Day_of_Week' in dataset.columns:
        day_counts = dataset.groupby('Day_of_Week').size().to_dict()
        peak_day = max(day_counts.items(), key=lambda x: x[1])
    else:
        day_counts = {}
        peak_day = (None, 0)
    
    return {
        "hourly_distribution": {int(k): int(v) for k, v in hour_counts.items()},
        "peak_hour": int(peak_hour[0]),
        "peak_hour_accidents": int(peak_hour[1]),
        "daily_distribution": {int(k): int(v) for k, v in day_counts.items()} if day_counts else None,
        "peak_day": int(peak_day[0]) if peak_day[0] is not None else None
    }


def get_weather_impact() -> Dict[str, Any]:
    """Analyze weather conditions impact"""
    if 'Weather_Conditions' not in dataset.columns:
        return {"error": "Weather data not available"}
    
    weather_severity = dataset.groupby('Weather_Conditions').agg({
        'Accident_Severity': ['count', 'mean']
    }).reset_index()
    weather_severity.columns = ['condition', 'accident_count', 'avg_severity']
    
    result = {}
    for _, row in weather_severity.iterrows():
        condition = int(row['condition']) if not pd.isna(row['condition']) else 'unknown'
        result[condition] = {
            "accident_count": int(row['accident_count']),
            "avg_severity": float(row['avg_severity'])
        }
    
    return result


def get_speed_limit_analysis() -> Dict[str, Any]:
    """Analyze accidents by speed limit"""
    if 'Speed_limit' not in dataset.columns:
        return {"error": "Speed limit data not available"}
    
    speed_analysis = dataset.groupby('Speed_limit').agg({
        'Accident_Severity': ['count', 'mean']
    }).reset_index()
    speed_analysis.columns = ['speed_limit', 'accident_count', 'avg_severity']
    
    result = {}
    for _, row in speed_analysis.iterrows():
        speed = int(row['speed_limit']) if not pd.isna(row['speed_limit']) else 'unknown'
        result[speed] = {
            "accident_count": int(row['accident_count']),
            "avg_severity": float(row['avg_severity'])
        }
    
    return result


def get_junction_analysis() -> Dict[str, Any]:
    """Analyze junction-related accidents"""
    if 'Junction_Detail' not in dataset.columns:
        return {"error": "Junction data not available"}
    
    junction_analysis = dataset.groupby('Junction_Detail').agg({
        'Accident_Severity': ['count', 'mean']
    }).reset_index()
    junction_analysis.columns = ['junction_type', 'accident_count', 'avg_severity']
    
    result = {}
    for _, row in junction_analysis.iterrows():
        junc_type = int(row['junction_type']) if not pd.isna(row['junction_type']) else 'unknown'
        result[junc_type] = {
            "accident_count": int(row['accident_count']),
            "avg_severity": float(row['avg_severity'])
        }
    
    return result


def get_casualty_statistics() -> Dict[str, Any]:
    """Get casualty statistics"""
    if 'Number_of_Casualties' not in dataset.columns:
        return {"error": "Casualty data not available"}
    
    return {
        "total_casualties": int(dataset['Number_of_Casualties'].sum()),
        "avg_per_accident": float(dataset['Number_of_Casualties'].mean()),
        "max_casualties": int(dataset['Number_of_Casualties'].max()),
        "accidents_with_multiple_casualties": int((dataset['Number_of_Casualties'] > 1).sum())
    }


def get_vehicle_analysis() -> Dict[str, Any]:
    """Analyze accidents by number of vehicles"""
    if 'Number_of_Vehicles' not in dataset.columns:
        return {"error": "Vehicle data not available"}
    
    vehicle_counts = dataset['Number_of_Vehicles'].value_counts().to_dict()
    
    return {
        "distribution": {int(k): int(v) for k, v in vehicle_counts.items()},
        "avg_vehicles": float(dataset['Number_of_Vehicles'].mean()),
        "multi_vehicle_accidents": int((dataset['Number_of_Vehicles'] > 1).sum())
    }


def get_top_risky_areas(limit: int = 10) -> List[Dict[str, Any]]:
    """Get most dangerous geographical areas"""
    if 'latitude' not in dataset.columns or 'longitude' not in dataset.columns:
        return [{"error": "Location data not available"}]
    
    dataset_copy = dataset.copy()
    dataset_copy['lat_rounded'] = dataset_copy['latitude'].round(2)
    dataset_copy['lon_rounded'] = dataset_copy['longitude'].round(2)
    
    location_stats = dataset_copy.groupby(['lat_rounded', 'lon_rounded']).agg({
        'Accident_Severity': ['count', 'mean']
    }).reset_index()
    location_stats.columns = ['lat', 'lon', 'accident_count', 'avg_severity']
    
    location_stats['risk_score'] = (
        location_stats['accident_count'] * 0.5 + 
        location_stats['avg_severity'] * 0.5
    )
    
    top_locations = location_stats.nlargest(limit, 'risk_score')
    
    result = []
    for _, row in top_locations.iterrows():
        result.append({
            "lat": float(row['lat']),
            "lon": float(row['lon']),
            "accident_count": int(row['accident_count']),
            "avg_severity": float(row['avg_severity']),
            "risk_score": float(row['risk_score'])
        })
    
    return result


def get_monthly_trends() -> Dict[str, Any]:
    """Get accident trends by month"""
    if 'Month' not in dataset.columns:
        return {"error": "Monthly data not available"}
    
    monthly_counts = dataset.groupby('Month').size().to_dict()
    monthly_severity = dataset.groupby('Month')['Accident_Severity'].mean().to_dict()
    
    return {
        "monthly_distribution": {int(k): int(v) for k, v in monthly_counts.items()},
        "monthly_severity": {int(k): float(v) for k, v in monthly_severity.items()},
        "peak_month": int(max(monthly_counts.items(), key=lambda x: x[1])[0]),
        "lowest_month": int(min(monthly_counts.items(), key=lambda x: x[1])[0])
    }


# ============================================================
# STRUCTURED RESPONSE FORMATTERS
# ============================================================

def format_severity_response(data: Dict[str, Any]) -> str:
    """Format severity distribution response"""
    return f"""Accident Severity Analysis

Out of {data['total_accidents']:,} total accidents:

- Fatal: {data['fatal']:,} accidents ({data['fatal_pct']}%)
- Serious: {data['serious']:,} accidents ({data['serious_pct']}%)
- Slight: {data['slight']:,} accidents ({data['slight_pct']}%)

Key Insight: {data['slight_pct']}% of accidents result in slight injuries, while fatal accidents account for {data['fatal_pct']}% of the total."""


def format_time_response(data: Dict[str, Any]) -> str:
    """Format time patterns response"""
    peak_hour = data['peak_hour']
    peak_accidents = data['peak_hour_accidents']
    
    hour_12 = peak_hour if peak_hour <= 12 else peak_hour - 12
    am_pm = "AM" if peak_hour < 12 else "PM"
    hour_12 = 12 if hour_12 == 0 else hour_12
    
    response = f"""Time Pattern Analysis

Peak Hour: {hour_12}:00 {am_pm} with {peak_accidents:,} accidents

Rush hours (7-9 AM and 4-6 PM) show significantly higher accident rates.

"""
    
    if data.get('peak_day'):
        days = ["", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        peak_day_name = days[data['peak_day']] if data['peak_day'] < len(days) else f"Day {data['peak_day']}"
        response += f"Most Dangerous Day: {peak_day_name}\n"
    
    response += "\nSafety Tip: Exercise extra caution during evening rush hour (5-6 PM)."
    
    return response


def format_weather_response(data: Dict[str, Any]) -> str:
    """Format weather impact response"""
    if "error" in data:
        return "Weather data is not available in the dataset."
    
    sorted_conditions = sorted(data.items(), key=lambda x: x[1]['accident_count'], reverse=True)
    top_condition = sorted_conditions[0] if sorted_conditions else None
    
    response = "Weather Impact Analysis\n\n"
    
    if top_condition:
        response += f"Most Common Condition: Weather code {top_condition[0]} with {top_condition[1]['accident_count']:,} accidents\n"
        response += f"Average Severity: {top_condition[1]['avg_severity']:.2f}\n\n"
    
    response += f"Analyzed {len(data)} different weather conditions.\n\n"
    response += "Note: Different weather codes represent varying conditions (clear, rain, fog, etc.)"
    
    return response


def format_speed_response(data: Dict[str, Any]) -> str:
    """Format speed limit analysis response"""
    if "error" in data:
        return "Speed limit data is not available in the dataset."
    
    sorted_speeds = sorted(
        [(k, v) for k, v in data.items() if k != 'error'],
        key=lambda x: x[1]['accident_count'],
        reverse=True
    )
    
    response = "Speed Limit Analysis\n\n"
    
    if len(sorted_speeds) >= 3:
        response += "Top 3 Speed Limits by Accident Count:\n\n"
        for i, (speed, stats) in enumerate(sorted_speeds[:3], 1):
            response += f"{i}. {speed} mph: {stats['accident_count']:,} accidents (Avg Severity: {stats['avg_severity']:.2f})\n"
    
    response += f"\n\nAnalyzed: {len(data)} different speed limit zones"
    
    return response


def format_junction_response(data: Dict[str, Any]) -> str:
    """Format junction analysis response"""
    if "error" in data:
        return "Junction data is not available in the dataset."
    
    total_accidents = sum(v['accident_count'] for v in data.values())
    
    response = "Junction Safety Analysis\n\n"
    response += f"Total Junction-Related Accidents: {total_accidents:,}\n\n"
    
    sorted_junctions = sorted(data.items(), key=lambda x: x[1]['accident_count'], reverse=True)
    
    if sorted_junctions:
        top_junction = sorted_junctions[0]
        response += f"Highest Risk: Junction type {top_junction[0]} with {top_junction[1]['accident_count']:,} accidents\n"
    
    response += "\nSafety Recommendation: Special attention needed at high-risk junction types."
    
    return response


def format_casualty_response(data: Dict[str, Any]) -> str:
    """Format casualty statistics response"""
    if "error" in data:
        return "Casualty data is not available in the dataset."
    
    return f"""Casualty Statistics

Total Casualties: {data['total_casualties']:,}
Average per Accident: {data['avg_per_accident']:.2f}
Maximum in Single Accident: {data['max_casualties']}
Multi-Casualty Accidents: {data['accidents_with_multiple_casualties']:,}

Key Finding: On average, each accident results in {data['avg_per_accident']:.1f} casualties. {data['accidents_with_multiple_casualties']:,} accidents involved multiple casualties, emphasizing the need for improved safety measures."""


def format_vehicle_response(data: Dict[str, Any]) -> str:
    """Format vehicle analysis response"""
    if "error" in data:
        return "Vehicle data is not available in the dataset."
    
    return f"""Vehicle Involvement Analysis

Average Vehicles per Accident: {data['avg_vehicles']:.2f}
Multi-Vehicle Accidents: {data['multi_vehicle_accidents']:,}

Key Insight: {data['multi_vehicle_accidents']:,} accidents involved more than one vehicle, suggesting the importance of maintaining safe following distances and situational awareness."""


def format_risky_areas_response(data: List[Dict[str, Any]]) -> str:
    """Format risky areas response"""
    if not data or "error" in data[0]:
        return "Location data is not available in the dataset."
    
    response = f"High-Risk Location Analysis\n\nIdentified {len(data)} high-risk areas:\n\n"
    
    for i, location in enumerate(data[:5], 1):
        response += f"{i}. Location {i}: {location['accident_count']} accidents (Risk Score: {location['risk_score']:.2f})\n"
        response += f"   Coordinates: ({location['lat']:.2f}, {location['lon']:.2f})\n\n"
    
    response += "Recommendation: Enhanced enforcement and safety measures recommended for these hotspots."
    
    return response


def format_monthly_response(data: Dict[str, Any]) -> str:
    """Format monthly trends response"""
    if "error" in data:
        return "Monthly data is not available in the dataset."
    
    month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    peak_month_name = month_names[data['peak_month']] if data['peak_month'] < len(month_names) else f"Month {data['peak_month']}"
    lowest_month_name = month_names[data['lowest_month']] if data['lowest_month'] < len(month_names) else f"Month {data['lowest_month']}"
    
    peak_count = data['monthly_distribution'][data['peak_month']]
    lowest_count = data['monthly_distribution'][data['lowest_month']]
    
    return f"""Monthly Accident Trends

Peak Month: {peak_month_name} with {peak_count:,} accidents
Lowest Month: {lowest_month_name} with {lowest_count:,} accidents

Seasonal Pattern: {((peak_count - lowest_count) / lowest_count * 100):.1f}% difference between peak and lowest months.

Insight: Weather conditions, holidays, and traffic patterns contribute to seasonal variations in accident rates."""


def format_overview_response(data: Dict[str, Any]) -> str:
    """Format general overview response"""
    severity = data.get('severity', {})
    time_data = data.get('time', {})
    casualties = data.get('casualties', {})
    
    response = f"""Road Safety Overview

Dataset Summary:
- Total Accidents: {severity.get('total_accidents', 'N/A'):,}
- Total Casualties: {casualties.get('total_casualties', 'N/A'):,}
- Peak Hour: {time_data.get('peak_hour', 'N/A')}:00 with {time_data.get('peak_hour_accidents', 'N/A'):,} accidents

Severity Breakdown:
- Fatal: {severity.get('fatal_pct', 0)}%
- Serious: {severity.get('serious_pct', 0)}%
- Slight: {severity.get('slight_pct', 0)}%

Key Insights:
Most accidents occur during evening rush hour, with the majority resulting in slight injuries. However, the {severity.get('fatal', 0):,} fatal and {severity.get('serious', 0):,} serious accidents highlight the critical need for continued safety improvements."""
    
    return response


def generate_structured_response(intent: str, data: Dict[str, Any]) -> str:
    """Generate structured response based on intent"""
    
    formatters = {
        "severity_distribution": format_severity_response,
        "time_patterns": format_time_response,
        "weather_impact": format_weather_response,
        "speed_analysis": format_speed_response,
        "junction_analysis": format_junction_response,
        "casualty_stats": format_casualty_response,
        "vehicle_analysis": format_vehicle_response,
        "risky_areas": format_risky_areas_response,
        "monthly_trends": format_monthly_response,
        "general_overview": format_overview_response
    }
    
    formatter = formatters.get(intent, lambda d: "Analysis complete. Please ask a specific question about the data.")
    return formatter(data)


# ============================================================
# QUERY PROCESSING
# ============================================================

def classify_query_intent(query: str) -> Dict[str, Any]:
    """Classify user query intent with LLM fallback to keywords"""
    
    classification_prompt = f"""
You are a query classifier. Classify this query into ONE intent.

Query: "{query}"

Intents: severity_distribution, time_patterns, weather_impact, speed_analysis, junction_analysis, casualty_stats, vehicle_analysis, risky_areas, monthly_trends, general_overview

Return ONLY JSON:
{{"intent": "intent_name", "confidence": 0.9, "needs_visualization": true, "visualization_type": "bar"}}
"""
    
    try:
        response = llm.invoke(classification_prompt)
        content = response.content.strip()
        
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"Classification error: {e}")
    
    # Fallback: Keyword matching
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['fatal', 'serious', 'slight', 'severity']):
        return {"intent": "severity_distribution", "confidence": 0.7, "needs_visualization": True, "visualization_type": "pie"}
    elif any(word in query_lower for word in ['time', 'hour', 'when', 'day']):
        return {"intent": "time_patterns", "confidence": 0.7, "needs_visualization": True, "visualization_type": "bar"}
    elif any(word in query_lower for word in ['month', 'seasonal', 'trend']):
        return {"intent": "monthly_trends", "confidence": 0.7, "needs_visualization": True, "visualization_type": "line"}
    elif any(word in query_lower for word in ['location', 'where', 'dangerous', 'hotspot', 'area']):
        return {"intent": "risky_areas", "confidence": 0.7, "needs_visualization": True, "visualization_type": "map"}
    elif any(word in query_lower for word in ['weather', 'rain', 'fog']):
        return {"intent": "weather_impact", "confidence": 0.7, "needs_visualization": True, "visualization_type": "bar"}
    elif any(word in query_lower for word in ['speed', 'mph']):
        return {"intent": "speed_analysis", "confidence": 0.7, "needs_visualization": True, "visualization_type": "bar"}
    elif any(word in query_lower for word in ['casualt', 'injur', 'death']):
        return {"intent": "casualty_stats", "confidence": 0.7, "needs_visualization": False, "visualization_type": None}
    else:
        return {"intent": "general_overview", "confidence": 0.5, "needs_visualization": False, "visualization_type": None}


def execute_analysis(intent: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute analysis based on intent"""
    
    analysis_map = {
        "severity_distribution": get_severity_distribution,
        "time_patterns": get_time_patterns,
        "weather_impact": get_weather_impact,
        "speed_analysis": get_speed_limit_analysis,
        "junction_analysis": get_junction_analysis,
        "casualty_stats": get_casualty_statistics,
        "vehicle_analysis": get_vehicle_analysis,
        "risky_areas": lambda: get_top_risky_areas(parameters.get('limit', 10)),
        "monthly_trends": get_monthly_trends,
    }
    
    if intent in analysis_map:
        return analysis_map[intent]()
    else:
        return {
            "severity": get_severity_distribution(),
            "time": get_time_patterns(),
            "casualties": get_casualty_statistics()
        }


def generate_natural_response(query: str, data: Dict[str, Any], intent: str) -> str:
    """Generate response with LLM fallback to structured"""
    
    response_prompt = f"""Answer this question concisely (under 150 words).

Question: "{query}"
Data: {json.dumps(data, indent=2)}

Provide clear, insightful response with specific numbers.
"""
    
    try:
        response = llm.invoke(response_prompt)
        llm_response = response.content.strip()
        
        if len(llm_response) > 50 and 'error' not in llm_response.lower():
            return llm_response
        else:
            raise Exception("Invalid LLM response")
            
    except Exception as e:
        print(f"LLM failed, using structured response: {e}")
        return generate_structured_response(intent, data)


def prepare_visualization(data: Dict[str, Any], viz_type: str, intent: str) -> Optional[Dict[str, Any]]:
    """Prepare visualization config"""
    
    if viz_type == "bar" and intent == "time_patterns" and "hourly_distribution" in data:
        return {
            "type": "bar",
            "data": {
                "labels": list(range(24)),
                "values": [data["hourly_distribution"].get(i, 0) for i in range(24)],
                "title": "Accidents by Hour of Day",
                "xLabel": "Hour",
                "yLabel": "Number of Accidents"
            }
        }
    elif viz_type == "pie" and intent == "severity_distribution":
        return {
            "type": "pie",
            "data": {
                "labels": ["Fatal", "Serious", "Slight"],
                "values": [data["fatal"], data["serious"], data["slight"]],
                "title": "Accident Severity Distribution"
            }
        }
    elif viz_type == "line" and intent == "monthly_trends" and "monthly_distribution" in data:
        months = sorted(data["monthly_distribution"].keys())
        month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return {
            "type": "line",
            "data": {
                "labels": [month_names[m] if m < len(month_names) else str(m) for m in months],
                "values": [data["monthly_distribution"][m] for m in months],
                "title": "Monthly Accident Trends",
                "xLabel": "Month",
                "yLabel": "Number of Accidents"
            }
        }
    elif viz_type == "map" and intent == "risky_areas" and isinstance(data, list):
        return {
            "type": "map",
            "data": {
                "locations": data,
                "title": "High-Risk Areas"
            }
        }
    
    return None


# ============================================================
# MAIN FUNCTION
# ============================================================

def process_safety_query(query: str) -> Dict[str, Any]:
    """Main query processing function"""
    
    try:
        classification = classify_query_intent(query)
        intent = classification.get("intent", "general_overview")
        parameters = classification.get("parameters", {})
        needs_viz = classification.get("needs_visualization", False)
        viz_type = classification.get("visualization_type", "table")
        
        analysis_data = execute_analysis(intent, parameters)
        natural_response = generate_natural_response(query, analysis_data, intent)
        
        visualization = None
        if needs_viz:
            visualization = prepare_visualization(analysis_data, viz_type, intent)
        
        return {
            "response": natural_response,
            "data": analysis_data,
            "intent": intent,
            "visualization": visualization
        }
        
    except Exception as e:
        print(f"Query processing error: {e}")
        return {
            "response": "I encountered an error processing your query. Please try rephrasing your question.",
            "data": {},
            "intent": "error",
            "visualization": None
        }