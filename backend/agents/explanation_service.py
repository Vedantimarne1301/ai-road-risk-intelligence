from langchain_groq import ChatGroq
import os
import json
import pandas as pd

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

def generate_explanation(prediction):
    """
    Generate analytical explanation for accident risk at a location.
    Only includes factors with known values. Omits unknown factors.
    """
    # Build factor-value context (omit missing/NaN)
    factor_values = ""
    factor_values_dict = {}
    for factor in prediction['top_factors']:
        value = prediction.get("factor_values", {}).get(factor)
        if value is not None and not (isinstance(value, float) and pd.isna(value)):
            factor_values += f"- {factor}: {value}\n"
            factor_values_dict[factor] = value

    prompt = f"""
You are an AI road safety analysis system.

Context:
- Accident Risk Level: {prediction['risk_level']}
- Risk Score: {prediction['risk_score']:.2f}
- Risk Urgency: {urgency_map.get(prediction['risk_level'], 'Unknown')}
- Top Factors with Values:
{factor_values if factor_values else '- No factor data available'}

Instructions:
1. Explain how the above factors contribute to accident risk at this location.
2. Use ONLY the provided factors; do NOT mention missing or unknown factors.
3. Keep explanation concise (3–4 lines), analytical, and professional.
4. Return output strictly in JSON format:

{{
  "risk_summary": "Concise explanation here",
  "primary_drivers": {list(factor_values_dict.keys())}
}}
"""
    response = llm.invoke(prompt)

    # Convert LLM output string → JSON
    try:
        return json.loads(response.content)
    except:
        return {
            "risk_summary": response.content,
            "primary_drivers": list(factor_values_dict.keys())
        }