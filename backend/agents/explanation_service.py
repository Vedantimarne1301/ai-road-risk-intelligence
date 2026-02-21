from langchain_groq import ChatGroq
import os
import json

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.1,
    max_tokens=250
)


def generate_explanation(prediction):

    prompt = f"""
You are an AI road safety analysis system.

Context:
- Accident Risk Level: {prediction['risk_level']}
- Risk Score: {prediction['risk_score']}
- Model Identified Risk Drivers: {prediction['top_factors']}

Instructions:
1. Use ONLY the provided risk drivers.
2. Do NOT assume weather, infrastructure, or geographic conditions unless listed.
3. Explain how the factors together increase accident risk.
4. Keep explanation within 3–4 lines.
5. Be analytical and professional.
6. No storytelling or speculation.

Return output strictly in JSON format:

{{
  "risk_summary": "Concise explanation here",
  "primary_drivers": ["factor1", "factor2", "factor3"]
}}
"""

    response = llm.invoke(prompt)

    # Convert LLM output string → JSON
    try:
        return json.loads(response.content)
    except:
        return {
            "risk_summary": response.content,
            "primary_drivers": prediction["top_factors"]
        }
