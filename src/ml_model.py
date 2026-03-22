import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import logging

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, accuracy_score

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


df= pd.read_csv("data/processed/change_impact.csv")
logger.info(f"Dataset shape: {df.shape}")
# Clean
df = df.dropna().drop_duplicates()

# Categorical features
categorical_cols = ["change_type", "owning_team", "environment"]

# Target column
target_col = "impact"

X_cat_raw = df[categorical_cols]
y = df[target_col]

encoder = OneHotEncoder(sparse_output=False)

# -----------------------------
# Encode categorical variables
# -----------------------------
# OneHotEncoder converts text categories into numeric columns
# handle_unknown='ignore' prevents errors if new categories appear later
encoder = OneHotEncoder(handle_unknown="ignore",  drop="first", sparse_output=False)
                        
# Fit encoder and transform categorical columns
X_cat_encoded = encoder.fit_transform(X_cat_raw)
# Get encoded feature names for readability
X = pd.DataFrame(X_cat_encoded, columns=encoder.get_feature_names_out(categorical_cols), index=df.index)

# Train-test split

X_train, X_test, y_train, y_test = train_test_split( X,y,test_size=0.20,random_state=42,stratify=y)

# Train model

rf_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    random_state=42,
    class_weight="balanced"
)

rf_model.fit(X_train, y_train)

# Predictions 
y_prob = rf_model.predict_proba(X_test)[:, 1]
threshold = 0.40
y_pred = (y_prob >= threshold).astype(int)
# Evaluation
accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)

logger.info(f"Accuracy: {accuracy:.4f}")
logger.info(f"AUC Score: {auc:.4f}")

logger.info("Classification Report:\n" + classification_report(y_test, y_pred))
logger.info("Confusion Matrix:\n" + str(confusion_matrix(y_test, y_pred)))

# Risk function
# -----------------------------
def risk_level(prob):
    if prob < 0.30:
        return "LOW"
    elif prob < 0.70:
        return "MEDIUM"
    else:
        return "HIGH"


# -----------------------------
# Prediction results table
# -----------------------------
logger.info("Creating prediction result summary...")

results = X_test.copy()
results["actual_impact"] = y_test.values
results["predicted_impact"] = y_pred
results["probability_of_failure"] = y_prob
results["risk"] = results["probability_of_failure"].apply(risk_level)

logger.debug("Sample predictions:\n" + str(
    results[["actual_impact", "predicted_impact", "probability_of_failure", "risk"]].head(10)
))

# Save artifacts
joblib.dump(rf_model, "rf_model.pkl")
joblib.dump(encoder, "encoder.pkl")
joblib.dump(X.columns.tolist(), "model_features.pkl")