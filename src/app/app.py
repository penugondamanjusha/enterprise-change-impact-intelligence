import joblib
import pandas as pd
import logging
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
import os 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load saved artifacts
BASE_DIR = Path(__file__).resolve().parents[2]
rf_model = joblib.load(os.path.join(BASE_DIR, "rf_model.pkl"))
encoder = joblib.load(os.path.join(BASE_DIR,"encoder.pkl"))
model_features = joblib.load(os.path.join(BASE_DIR,"model_features.pkl"))

logger.info("Model artifacts loaded successfully.")

# Load saved artifacts

app = FastAPI(
    title="Change Risk Prediction API",
    description="Predicts deployment failure probability for a new change",
    version="1.0.0"
)

# Input schema

class ChangeRequest(BaseModel):
    change_type: str
    owning_team: str
    environment: str

# Helper functions

def risk_level(prob: float) -> str:
    
    if prob < 0.30:
        return "LOW"
    elif prob < 0.70:
        return "MEDIUM"
    else:
        return "HIGH"

def deployment_decision(prob: float, threshold: float = 0.40) -> str:
    return "BLOCK" if prob >= threshold else "ALLOW"

@app.get("/")
def home():
    return {"message": "Change Risk Prediction API is running"}


@app.post("/predict")
def predict_change(request: ChangeRequest):
    logger.info("Received prediction request.")

    # Convert request into DataFrame
    input_df = pd.DataFrame([{
        "change_type": request.change_type,
        "owning_team": request.owning_team,
        "environment": request.environment
    }])

    # Encode input using trained encoder
    encoded_input = encoder.transform(input_df)
    encoded_feature_names = encoder.get_feature_names_out(
        ["change_type", "owning_team", "environment"]
    )

    encoded_df = pd.DataFrame(
        encoded_input,
        columns=encoded_feature_names
    )

    # Reindex to match training feature order exactly
    encoded_df = encoded_df.reindex(columns=model_features, fill_value=0)

    # Predict probability
    probability = rf_model.predict_proba(encoded_df)[:, 1][0]

    # Threshold-based binary prediction
    threshold = 0.40
    prediction = int(probability >= threshold)

    # Business-friendly outputs
    risk = risk_level(probability)
    decision = deployment_decision(probability, threshold=threshold)

    logger.info(
        f"Prediction completed | probability={probability:.4f}, "
        f"risk={risk}, decision={decision}"
    )

    return {
        "probability_of_failure": round(float(probability), 4),
        "prediction": prediction,
        "risk": risk,
        "decision": decision,
        "threshold_used": threshold
    }