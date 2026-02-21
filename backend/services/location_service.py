import pandas as pd
import numpy as np
import joblib

# Load processed dataset used for training
# IMPORTANT: This should be the SAME dataset used to train model
DATA_PATH = "model//processed_dataset.csv"

dataset = pd.read_csv(DATA_PATH)

# Load feature columns used during training
feature_columns = joblib.load("model//model_features.pkl")


# ---------------------------------------------------------
# Helper Function: Find nearest accident location
# ---------------------------------------------------------
def find_nearest_location(lat, lon):
    """
    Finds the nearest accident record based on latitude & longitude
    """

    # Euclidean distance (fast enough for hackathon scale)
    distances = (
        (dataset["latitude"] - lat) ** 2 +
        (dataset["longitude"] - lon) ** 2
    )

    nearest_index = distances.idxmin()
    nearest_row = dataset.loc[nearest_index]

    return nearest_row


# ---------------------------------------------------------
# Main Function: Convert location → model features
# ---------------------------------------------------------
def get_features_from_location(lat, lon):
    """
    Converts map location into model-ready feature dictionary
    """

    nearest_accident = find_nearest_location(lat, lon)

    # Extract only model features
    feature_dict = {}

    for col in feature_columns:
        if col in nearest_accident:
            feature_dict[col] = nearest_accident[col]
        else:
            feature_dict[col] = np.nan

    return feature_dict
