<div align="center">

# 🩺 SepsisGuard

**Clinical Sepsis Risk Assessment — ML-Powered Decision Support**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5%2B-orange?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/tests-23%20passed-brightgreen?logo=pytest)](tests/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[Overview](#overview) · [Features](#features) · [Architecture](#architecture) · [Quick Start](#quick-start) · [API](#api-reference) · [Development](#development) · [Limitations](#limitations)

</div>

---

## Overview

Sepsis is a life-threatening organ dysfunction caused by a dysregulated response to infection.  
Early identification is critical — every hour of delayed treatment increases mortality.

**SepsisGuard** is a web-based clinical decision-support tool that uses a machine-learning model trained on real ICU data to estimate a patient's risk of sepsis in real time.  
Clinicians enter 12 routine vital-sign and laboratory values; the model returns a risk score (0–100 %) and a binary classification (High / Low Risk).

> ⚠️ **Intended for educational and research purposes only.**  
> SepsisGuard is not a licensed medical device and must not be used as a substitute for professional clinical judgement.

---

## Features

| Feature | Description |
|---|---|
| **Real-time risk scoring** | Instant sepsis probability from 12 clinical inputs |
| **Three sample patients** | Healthy / Early Warning / Critical presets for demonstration |
| **Animated risk gauge** | Circular progress ring with colour-coded severity |
| **Input validation** | Server-side range checks with descriptive error messages |
| **Health-check endpoint** | `/health` endpoint for monitoring and CI |
| **Responsive UI** | Works on desktop and tablet browsers |

---

## Architecture

```
SepsisGuard/
├── app.py                  # Flask application — routes, validation, inference
├── train_model.py          # Model training pipeline (Random Forest)
├── prepare_data.py         # Raw-data aggregation (time-series → per-patient)
├── requirements.txt        # Minimal, pinned Python dependencies
├── sepsis_model.pkl        # Trained model (joblib format, committed as release artifact)
│
├── templates/
│   └── index.html          # Single-page Jinja2 template
│
├── static/
│   ├── css/style.css       # IBM Plex design system, responsive layout
│   └── js/script.js        # Fetch API calls, ring animation, preset loader
│
├── scripts/
│   └── explore_data.py     # Development EDA helper (not part of the app)
│
├── tests/
│   └── test_app.py         # 23 pytest tests covering routes + validation
│
└── .github/
    └── workflows/
        └── ci.yml          # GitHub Actions — install → lint → test on every push
```

### How it Works

```
User Input (12 vitals/labs)
        │
        ▼
Flask /predict (POST JSON)
        │
        ├── Server-side range validation
        │
        ▼
pandas DataFrame  ──►  RandomForestClassifier.predict_proba()
                                │
                                ▼
              { prediction: 0|1, probability: 0-100 }
                                │
                                ▼
                    Frontend ring animation + label
```

**Model:** Random Forest Classifier (200 trees, `class_weight="balanced"`)  
**Training data:** PhysioNet Computing in Cardiology Challenge 2019 — ICU time-series data, averaged per patient  
**Features (12):** HR, O₂ Saturation, Temperature, Systolic BP, MAP, Respiratory Rate, BUN, Creatinine, Glucose, WBC, Age, Gender

---

## Quick Start

### Prerequisites

- Python 3.10 or newer
- pip

### 1. Clone the repository

```bash
git clone https://github.com/chillieeee/Sepsis-Guard-.git
cd Sepsis-Guard-
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify the model file is present

```bash
ls sepsis_model.pkl      # should exist (committed in this repo)
```

> If you need to retrain the model from scratch, see [Retraining the Model](#retraining-the-model).

### 5. Run the application

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## Configuration

SepsisGuard uses environment variables for configuration. Copy `.env.example` and edit as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `FLASK_DEBUG` | `1` | Set to `0` for production |
| `PORT` | `5000` | TCP port the server listens on |
| `MODEL_PATH` | `sepsis_model.pkl` | Path to the trained model file |

---

## API Reference

### `GET /`

Returns the main assessment interface (HTML).

---

### `GET /health`

Lightweight health check for monitoring.

**Response 200**

```json
{ "status": "ok", "model_loaded": true }
```

---

### `POST /predict`

Run a sepsis risk assessment.

**Request body** (JSON)

```json
{
  "HR":         72,
  "O2Sat":      98,
  "Temp":       37.0,
  "SBP":        120,
  "MAP":        85,
  "Resp":       16,
  "BUN":        15.0,
  "Creatinine": 1.0,
  "Glucose":    100.0,
  "WBC":        7.0,
  "Age":        50,
  "Gender":     0
}
```

**Gender encoding:** `0` = Female, `1` = Male

**Response 200**

```json
{ "prediction": 0, "probability": 12.4 }
```

`prediction`: `0` = Low Risk, `1` = High Risk  
`probability`: estimated sepsis probability as a percentage (0–100)

**Error Responses**

| Code | Reason |
|---|---|
| `400` | Missing field, non-numeric value, or value outside clinical range |
| `500` | Model not loaded |

---

## Development

### Running Tests

```bash
pytest tests/ -v
```

Expected: **23 passed**.

### Project Scripts

| Script | Purpose |
|---|---|
| `prepare_data.py` | Aggregate raw PhysioNet CSV into `patient_summary.csv` |
| `train_model.py` | Train the classifier and save `sepsis_model.pkl` |
| `scripts/explore_data.py` | Quick EDA — print dataset statistics |

### Retraining the Model

The raw dataset is not included in this repository due to its size (54 MB). To retrain:

1. Download the dataset from [PhysioNet](https://physionet.org/content/challenge-2019/1.0.0/) and save it as `Dataset.csv` in the project root.
2. Run the data preparation step:
   ```bash
   python prepare_data.py
   ```
3. Train the model:
   ```bash
   python train_model.py
   ```

The classification report and AUC-ROC score will be printed to the console.

---

## Continuous Integration

Every push and pull request triggers the GitHub Actions workflow (`.github/workflows/ci.yml`):

1. Install Python dependencies
2. Run all 23 pytest tests

---

## Limitations

- **Educational use only** — not validated for clinical deployment.
- **Patient averaging** — the model is trained on per-patient mean vital signs, not raw time-series; temporal dynamics are not captured.
- **Static model** — the classifier is not retrained on new data automatically.
- **Binary output** — the model produces a single probability score; it does not provide explanations or feature importances in the UI.
- **Dataset bias** — performance may not generalise to patient populations outside the PhysioNet 2019 ICU cohort.

---

## Future Improvements

- [ ] SHAP-based feature importance explanations in the UI
- [ ] Time-series input support for trend analysis
- [ ] Authentication and session management for multi-user deployments
- [ ] Docker image for one-command deployment
- [ ] Structured logging with request tracing

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "feat: add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## Acknowledgements

- Dataset: [PhysioNet / Computing in Cardiology Challenge 2019](https://physionet.org/content/challenge-2019/1.0.0/)
- Reyna et al. (2020) — *Early Prediction of Sepsis from Clinical Data*
- Font: [IBM Plex Sans & IBM Plex Mono](https://github.com/IBM/plex) (OFL-1.1)
