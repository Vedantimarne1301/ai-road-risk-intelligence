from agents.explanation_service import generate_explanation
from agents.agent_recommendation import generate_recommendations

def agent_pipeline(prediction):

    explanation = generate_explanation(prediction)
    recommendation = generate_recommendations(prediction)

    prediction["explanation"] = explanation
    prediction["recommendation"] = recommendation

    return prediction
