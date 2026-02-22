from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
from services.predict import predict_pipeline
from services.location_service import get_features_from_location
from agents.agent_controller import agent_pipeline
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  
from services.heatmap_service import get_heatmap_data, get_clustered_heatmap_data
from services.dashboard_service import (
    get_dashboard_statistics,
    get_risk_factors_distribution,
    get_top_risky_locations,
    get_severity_by_conditions,
    get_geographical_distribution,
    get_time_trends
)

app = FastAPI(title="AI Road Risk Prediction API")


# ---------------------------------------------------
# CORS (IMPORTANT for React Frontend)
# ---------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change later in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AIQuery(BaseModel):
    question: str


@app.post("/ai_safety_chat")
def ai_safety_chat(data: AIQuery):
    try:
        from agents.safety_agent import safety_agent_pipeline

        answer = safety_agent_pipeline({
            "risk_level": "General",
            "risk_score": 0,
            "top_factors": []
        }, custom_question=data.question)

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------
# NEW: /ask-safety-ai endpoint (simulated AI response)
# ---------------------------------------------------
class Question(BaseModel):
    question: str

@app.post("/ask-safety-ai")
async def ask_safety_ai(data: Question):
    response_text = f"""
    AI Risk Analysis:
    Based on your query: "{data.question}"
    • Consider speed limit enforcement.
    • Increase traffic monitoring during peak hours.
    • Deploy traffic police in high-risk zones.
    • Improve road lighting and signage.
    This is a simulated AI response.
    """
    return {
        "answer": response_text.strip()
    }


# ---------------------------------------------------
# Request Model (Manual Input)
# ---------------------------------------------------
class AccidentInput(BaseModel):
    Number_of_Vehicles: float
    Number_of_Casualties: float
    Speed_limit: float
    Junction_Detail: float
    Light_Conditions: float | None = None
    Weather_Conditions: float | None = None


# ---------------------------------------------------
# Health Check
# ---------------------------------------------------
@app.get("/")
def root():
    return {"message": "AI Road Risk Prediction API Running"}


# ===================================================
# DASHBOARD ENDPOINTS
# ===================================================

@app.get("/dashboard/statistics")
def dashboard_statistics():
    """
    Returns overall accident statistics for dashboard
    Includes: total accidents, casualties, severity distribution, etc.
    """
    try:
        return get_dashboard_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/risk-factors")
def risk_factors():
    """
    Returns distribution of various risk factors
    Includes: weather, light conditions, road surface, speed limits
    """
    try:
        return get_risk_factors_distribution()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/risky-locations")
def risky_locations(limit: int = 10):
    """
    Returns top risky locations with highest accident rates
    Query parameter: limit (default: 10, max: 50)
    """
    try:
        if limit > 50:
            limit = 50
        return get_top_risky_locations(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/severity-analysis")
def severity_analysis():
    """
    Returns severity breakdown by different conditions
    Includes analysis by: speed, hour, day of week, weather, vehicle count
    """
    try:
        return get_severity_by_conditions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/geo-distribution")
def geo_distribution():
    """
    Returns geographical distribution of accidents
    Shows accident hotspots across different regions
    """
    try:
        return get_geographical_distribution()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/time-trends")
def time_trends():
    """
    Returns accident trends over time
    Includes: monthly, hourly, and daily patterns
    """
    try:
        return get_time_trends()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================
# HEATMAP ENDPOINTS
# ===================================================

@app.get("/risk_heatmap")
def risk_heatmap(sample_size: int = 1000, severity: int | None = None):
    """
    Returns heatmap data for accident visualization
    Query parameters:
    - sample_size: Number of points to return (default: 1000)
    - severity: Filter by severity (0=Fatal, 1=Serious, 2=Slight)
    """
    try:
        if sample_size > 5000:
            sample_size = 5000  # Prevent overload
        return get_heatmap_data(sample_size, severity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/risk_heatmap_clustered")
def risk_heatmap_clustered(grid_size: float = 0.05):
    """
    Returns clustered heatmap data (better performance)
    Query parameter: grid_size (default: 0.05 degrees ≈ 5.5km)
    """
    try:
        if grid_size < 0.01:
            grid_size = 0.01
        if grid_size > 0.5:
            grid_size = 0.5
        return get_clustered_heatmap_data(grid_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================
# PREDICTION ENDPOINTS
# ===================================================

def format_response(agent_output):
    """
    Ensures frontend always receives the same response structure
    """
    return {
        "risk_level": agent_output.get("risk_level"),
        "risk_score": agent_output.get("risk_score"),
        "explanation": {
            "risk_summary":
                agent_output.get("explanation", {}).get("risk_summary", []),
            "primary_drivers":
                agent_output.get("explanation", {}).get("primary_drivers", [])
        },
        "recommendation": {
            "recommended_actions":
                agent_output.get("recommendation", {}).get(
                    "recommended_actions", []
                )
        }
    }


@app.post("/predict")
def predict(data: AccidentInput):
    """
    Manual prediction with provided accident features
    """
    try:
        input_dict = data.dict()

        # ML Prediction
        prediction = predict_pipeline(input_dict)

        # AI Agents
        agent_output = agent_pipeline(prediction)

        return format_response(agent_output)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict_location")
def predict_location(lat: float, lon: float):
    """
    Location-based prediction using latitude and longitude
    Finds nearest accident and predicts risk
    """
    try:
        # Location → model features
        features = get_features_from_location(lat, lon)

        if features is None:
            raise HTTPException(
                status_code=404,
                detail="No nearby accident data found"
            )

        # ML Prediction
        prediction = predict_pipeline(features)

        # AI Agents
        agent_output = agent_pipeline(prediction)

        return format_response(agent_output)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))