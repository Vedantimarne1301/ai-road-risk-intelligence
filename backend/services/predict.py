import joblib
import pandas as pd
import numpy as np
import shap

# Load model & features
model = joblib.load("model/accident_risk_xgb_model.pkl")
feature_columns = joblib.load("model/model_features.pkl")

explainer = shap.TreeExplainer(model)

# Excluded from SHAP explanation
EXCLUDED_FEATURES = [
    "latitude",
    "longitude",
    "Accident_Index",
    "Local_Authority_(District)",
    "LSOA_of_Accident_Location"
]

def prepare_input(input_dict):
    """
    Convert input dict into model-ready dataframe
    """
    df = pd.DataFrame([input_dict])
    for col in feature_columns:
        if col not in df.columns:
            df[col] = np.nan
    df = df[feature_columns]
    return df


def predict_severity(input_dict):
    """
    Predict accident severity
    Model mapping: 0=Fatal, 1=Serious, 2=Slight
    """
    X = prepare_input(input_dict)
    pred_class = model.predict(X)[0]
    pred_prob = model.predict_proba(X)[0]
    confidence = float(pred_prob[pred_class])
    return X, int(pred_class), confidence, pred_prob


def get_shap_explanation(X, pred_class):
    """
    Get SHAP explanation for the predicted class
    """
    shap_values = explainer.shap_values(X)
    shap_values_class = np.abs(shap_values[0][:, pred_class])
    shap_df = pd.DataFrame({
        "feature": X.columns,
        "impact": shap_values_class
    })
    shap_df = shap_df.sort_values(by="impact", ascending=False)
    shap_df = shap_df[~shap_df["feature"].isin(EXCLUDED_FEATURES)]
    top_features = shap_df.head(5)["feature"].tolist()
    return top_features


def predict_pipeline(input_dict):
    """
    Full prediction pipeline with correct risk mapping
    """
    X, pred_class, confidence, pred_prob = predict_severity(input_dict)
    top_factors = get_shap_explanation(X, pred_class)

    # Correct risk mapping
    risk_map = {0: "High", 1: "Medium", 2: "Low"}

    return {
        "risk_level": risk_map[pred_class],
        "risk_score": confidence,
        "severity_class": pred_class,
        "top_factors": top_factors,
        "class_probabilities": {
            "high": float(pred_prob[0]),
            "medium": float(pred_prob[1]),
            "low": float(pred_prob[2])
        }
    }