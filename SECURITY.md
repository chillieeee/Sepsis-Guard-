# Security Policy

## Scope

SepsisGuard is an **educational research project**. It is not a production medical system and does not process or store real patient data. Nevertheless, we take security seriously.

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main` branch | ✅ Yes |
| Older releases | ❌ No |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report security concerns privately by emailing: **jeboshanj@gmail.com**

Include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- (Optional) A suggested fix

We aim to acknowledge reports within 48 hours and resolve confirmed issues within 14 days.

## Known Limitations

- The application runs in **development mode** by default (`FLASK_DEBUG=1`). Always set `FLASK_DEBUG=0` in any public-facing deployment.
- No authentication or rate-limiting is implemented. Do not expose this application to the public internet without adding those controls.
- The model file (`sepsis_model.pkl`) is a joblib pickle; only load model files from trusted sources.
