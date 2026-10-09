# Changelog

All notable changes to SepsisGuard are documented here.  
This project follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2025-10-09

### Added
- Flask web application (`app.py`) with `/`, `/predict`, and `/health` endpoints
- Random Forest Classifier trained on PhysioNet Sepsis 2019 dataset
- Per-patient data aggregation pipeline (`prepare_data.py`)
- Professional model training pipeline (`train_model.py`) with AUC-ROC reporting
- Animated risk-gauge UI with IBM Plex design system
- Three sample patient presets (Healthy, Early Warning, Critical)
- Server-side input validation with clinically plausible ranges for all 12 features
- 23-test pytest suite covering routes, validation, and configuration
- GitHub Actions CI workflow (install → test on every push/PR)
- `.gitignore` excluding venv, secrets, and large data files
- `requirements.txt` with minimal pinned dependencies
- `.env.example` for safe configuration
- `LICENSE` (MIT)
- `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`
- `scripts/explore_data.py` — EDA helper script

### Changed
- `app.py`: removed `debug=True` hardcoding; now controlled by `FLASK_DEBUG` env var
- `app.py`: added server-side range validation for all feature inputs
- `app.py`: added `/health` endpoint for monitoring
- `app.py`: improved error messages (specific field names reported)
- `train_model.py`: refactored into functions with proper logging and AUC reporting
- `prepare_data.py`: refactored with logging, validation, and exit-on-error
- `explore_data.py`: moved to `scripts/` (development helper, not app code)

### Fixed
- Flask `__version__` deprecation warning suppressed by removing direct version access
- Missing `get_json(silent=True)` causing 500 on malformed request bodies
- Large binary/data files excluded from version control via `.gitignore`
