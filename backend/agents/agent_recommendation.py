from langchain_groq import ChatGroq
import os
import json

# Initialize the LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.1,
    max_tokens=250
)

# Mapping for urgency based on risk level
urgency_map = {
    "High": "urgent attention required",
    "Medium": "moderate risk, needs monitoring",
    "Low": "minor risk, precautionary measures"
}

def generate_recommendations(prediction):
    """
    AI-based recommendation generator using SHAP factors.
    Produces structured, location-specific, actionable outputs.
    """
    # Build factor-value context
    factor_values = ""
    for factor in prediction['top_factors']:
        value = prediction.get("factor_values", {}).get(factor, "Unknown")
        factor_values += f"- {factor}: {value}\n"

    prompt = f"""
You are an intelligent traffic safety planning assistant.

Context:
- Accident Risk Level: {prediction['risk_level']}
- Risk Score: {prediction['risk_score']:.2f}
- Risk Urgency: {urgency_map.get(prediction['risk_level'], 'Unknown')}
- ML Identified Risk Drivers with Values:
{factor_values}

Instructions:
1. Provide exactly 3 recommendations for this location.
2. Each recommendation must directly address one or more listed risk drivers.
3. Focus only on infrastructure, traffic engineering, or traffic control improvements.
4. Keep each recommendation to one short sentence.
5. Do NOT add assumptions beyond given factors.
6. Avoid generic advice.
7. Return output strictly in JSON format:

{{
  "recommended_actions": [
    "Action 1",
    "Action 2",
    "Action 3"
  ]
}}
"""

    response = llm.invoke(prompt)

    # Convert LLM output → JSON safely
    try:
        return json.loads(response.content)
    except:
        return {
            "recommended_actions": [
                response.content
            ]
        }