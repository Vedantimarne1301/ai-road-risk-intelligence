import joblib
import pandas as pd
import numpy as np
import shap


# ---------------------------------------------------
# Load Model & Metadata
# ---------------------------------------------------
model = joblib.load("model/accident_risk_xgb_model.pkl")
feature_columns = joblib.load("model/model_features.pkl")

explainer = shap.TreeExplainer(model)


# ---------------------------------------------------
# Features NOT suitable for explanation
# (Spatial or administrative identifiers)
# ---------------------------------------------------
EXCLUDED_FEATURES = [
    "latitude",
    "longitude",
    "Accident_Index",
    "Local_Authority_(District)",
    "LSOA_of_Accident_Location"
]


# ---------------------------------------------------
# Prepare Input for Model
# ---------------------------------------------------
def prepare_input(input_dict):
    """
    Converts incoming data into model-ready dataframe
    """

    df = pd.DataFrame([input_dict])

    # Ensure all training columns exist
    for col in feature_columns:
        if col not in df.columns:
            df[col] = np.nan

    # Maintain training column order
    df = df[feature_columns]

    return df


# ---------------------------------------------------
# Model Prediction
# ---------------------------------------------------
def predict_severity(input_dict):

    X = prepare_input(input_dict)

    pred_class = model.predict(X)[0]
    pred_prob = model.predict_proba(X)[0]

    confidence = float(np.max(pred_prob))

    return X, int(pred_class), confidence


# ---------------------------------------------------
# SHAP Explanation
# ---------------------------------------------------
def get_shap_explanation(X, pred_class):

    shap_values = explainer.shap_values(X)

    # SHAP values for predicted class
    shap_values_class = shap_values[0][:, pred_class]

    shap_df = pd.DataFrame({
        "feature": X.columns,
        "impact": np.abs(shap_values_class)
    })

    # Sort by importance
    shap_df = shap_df.sort_values(by="impact", ascending=False)

    # Remove non-causal features
    shap_df = shap_df[
        ~shap_df["feature"].isin(EXCLUDED_FEATURES)
    ]

    # Top contributing factors
    top_features = shap_df.head(5)["feature"].tolist()

    return top_features


# ---------------------------------------------------
# Main Prediction Pipeline
# ---------------------------------------------------
def predict_pipeline(input_dict):

    X, pred_class, confidence = predict_severity(input_dict)

    top_factors = get_shap_explanation(X, pred_class)

    risk_map = {
        0: "Low",
        1: "Medium",
        2: "High"
    }

    return {
        "risk_level": risk_map[pred_class],
        "risk_score": confidence,
        "severity_class": pred_class,
        "top_factors": top_factors
    }
