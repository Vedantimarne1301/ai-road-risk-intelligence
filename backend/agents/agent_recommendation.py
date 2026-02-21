from langchain_groq import ChatGroq
import os
import json

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=GROQ_API_KEY,
    temperature=0.1,
    max_tokens=250
)


def generate_recommendations(prediction):
    """
    AI-based recommendation generator using SHAP factors.
    Produces structured, short, actionable outputs.
    """

    risk_level = prediction["risk_level"]
    risk_score = prediction["risk_score"]
    top_factors = prediction["top_factors"]

    prompt = f"""
You are an intelligent traffic safety planning assistant.

Context:
- Accident Risk Level: {risk_level}
- Risk Score: {risk_score}
- ML Identified Risk Drivers: {top_factors}

Instructions:
1. Provide exactly 3 recommendations.
2. Each recommendation must directly address one or more listed risk drivers.
3. Focus only on infrastructure, traffic engineering, or traffic control improvements.
4. Keep each recommendation to one short sentence.
5. Do NOT add assumptions beyond given factors.
6. Avoid generic advice.

Return output strictly in JSON format:

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
