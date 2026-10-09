"""
SepsisGuard — Clinical Sepsis Risk Assessment Web Application
=============================================================
A Flask web application that uses a trained Random Forest classifier
to estimate a patient's risk of sepsis from 12 vital-sign and lab inputs.

Usage:
    python app.py                  # development (debug mode)
    flask run --host 0.0.0.0       # production (set FLASK_DEBUG=0)
"""

import os
import logging

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
app = Flask(__name__)

# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
MODEL_PATH = os.environ.get("MODEL_PATH", "sepsis_model.pkl")

model = None
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        logger.info("Model loaded successfully from '%s'.", MODEL_PATH)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to load model from '%s': %s", MODEL_PATH, exc)
else:
    logger.warning(
        "Model file '%s' not found.  Run train_model.py to generate it.", MODEL_PATH
    )

# ---------------------------------------------------------------------------
# Feature definitions
# ---------------------------------------------------------------------------
FEATURES = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "Resp",
    "BUN", "Creatinine", "Glucose", "WBC", "Age", "Gender",
]

# Clinically plausible ranges for basic server-side validation.
# Values outside these bounds are likely data-entry errors.
FEATURE_RANGES = {
    "HR":         (20,   300),
    "O2Sat":      (50,   100),
    "Temp":       (30.0, 45.0),
    "SBP":        (40,   300),
    "MAP":        (20,   200),
    "Resp":       (4,    60),
    "BUN":        (1.0,  200.0),
    "Creatinine": (0.1,  20.0),
    "Glucose":    (20.0, 800.0),
    "WBC":        (0.1,  200.0),
    "Age":        (0,    130),
    "Gender":     (0,    1),
}

# Pre-loaded example patients (also used by the front-end)
PRESETS = {
    "healthy": dict(
        HR=72, O2Sat=99, Temp=36.8, SBP=118, MAP=88, Resp=14,
        BUN=12.0, Creatinine=0.9, Glucose=95.0, WBC=6.5, Age=35, Gender=0,
    ),
    "warning": dict(
        HR=105, O2Sat=94, Temp=38.4, SBP=100, MAP=70, Resp=24,
        BUN=22.0, Creatinine=1.4, Glucose=140.0, WBC=13.0, Age=62, Gender=1,
    ),
    "critical": dict(
        HR=130, O2Sat=88, Temp=39.5, SBP=80, MAP=55, Resp=32,
        BUN=45.0, Creatinine=2.8, Glucose=180.0, WBC=19.0, Age=74, Gender=1,
    ),
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Serve the main assessment interface."""
    return render_template("index.html", presets=PRESETS)


@app.route("/health")
def health():
    """Lightweight health-check endpoint for monitoring / CI verification."""
    return jsonify({"status": "ok", "model_loaded": model is not None})


@app.route("/predict", methods=["POST"])
def predict():
    """
    Accept a JSON body with the 12 feature values, run the model, and return
    the binary prediction (0/1) together with the probability score (0–100 %).

    Returns
    -------
    200  {"prediction": int, "probability": float}
    400  {"error": str}   — missing / non-numeric / out-of-range inputs
    500  {"error": str}   — model unavailable
    """
    if model is None:
        return jsonify({"error": "Model not loaded. Run train_model.py first."}), 500

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    # --- Parse & validate ---
    row = {}
    for feature in FEATURES:
        if feature not in data:
            return jsonify({"error": f"Missing required field: '{feature}'."}), 400
        try:
            value = float(data[feature])
        except (ValueError, TypeError):
            return jsonify({"error": f"Field '{feature}' must be a number."}), 400

        lo, hi = FEATURE_RANGES[feature]
        if not (lo <= value <= hi):
            return jsonify(
                {"error": f"'{feature}' value {value} is outside the valid range ({lo}–{hi})."}
            ), 400
        row[feature] = value

    # --- Inference ---
    try:
        input_df = pd.DataFrame([row])
        prediction = int(model.predict(input_df)[0])
        probability = float(model.predict_proba(input_df)[0][1])
    except Exception as exc:  # noqa: BLE001
        logger.exception("Inference error: %s", exc)
        return jsonify({"error": "An internal error occurred during prediction."}), 500

    return jsonify({"prediction": prediction, "probability": round(probability * 100, 1)})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # debug=True is intentional for local development only.
    # For production, use: gunicorn app:app  (or flask run with FLASK_DEBUG=0)
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug, port=port)
