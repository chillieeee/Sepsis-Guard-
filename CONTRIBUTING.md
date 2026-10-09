# Contributing to SepsisGuard

Thank you for your interest in contributing! This document outlines the process for reporting issues and submitting improvements.

## Code of Conduct

Please be respectful and constructive in all interactions.

## How to Report a Bug

1. Check [existing issues](https://github.com/chillieeee/Sepsis-Guard-/issues) first.
2. Open a new issue using the **Bug Report** template.
3. Include:
   - Steps to reproduce the problem
   - Expected vs. actual behaviour
   - Python version, OS, and dependency versions (`pip freeze`)

## How to Suggest a Feature

Open an issue using the **Feature Request** template and describe:
- The problem you are trying to solve
- The proposed solution
- Any alternatives you have considered

## Development Workflow

### 1. Fork & Clone

```bash
git clone https://github.com/<your-username>/Sepsis-Guard-.git
cd Sepsis-Guard-
```

### 2. Set Up Your Environment

```bash
python -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install pytest
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/descriptive-branch-name
```

### 4. Make Your Changes

- Follow the existing code style (PEP 8, meaningful docstrings).
- Keep functions focused and well-named.
- Do not commit large binary files (datasets, notebooks).
- Do not commit secrets or credentials.

### 5. Write or Update Tests

All new behaviour should be covered by tests in `tests/`. Run the full suite before committing:

```bash
pytest tests/ -v
```

All 23 existing tests must continue to pass.

### 6. Commit and Push

Use clear, conventional commit messages:

```
feat: add SHAP feature importance panel
fix: handle NaN in prediction input
docs: update README API section
```

### 7. Open a Pull Request

- Target the `main` branch.
- Describe what changed and why.
- Reference any related issues (`Closes #42`).
- The CI pipeline must pass before merging.

## Important Note on Medical Claims

SepsisGuard is an educational project. Pull requests must not introduce claims about clinical accuracy, diagnostic capability, or patient safety unless backed by peer-reviewed evidence and appropriate regulatory consideration.
