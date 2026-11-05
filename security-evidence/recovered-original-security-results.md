# Recovered original security evidence

This section was recovered from the earlier `feature/backend-model-api` README so the team's original security work is not lost. It records the environment and dependency state at the time of that scan. Later dependency upgrades and security-header changes supersede some versions and findings; the current README and `security-evidence/README.md` describe the final submitted state.

### Defence 2: Intermediate Misconfiguration and Vulnerable Dependency Protection

**Configuration and Secrets:** Secrets and configurations are kept out of source code via `pydantic-settings` and a local `.env` file. Debug mode is specifically disabled to avoid stack trace leaks. We created a custom middleware that adds standard security headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`) into every HTTP response.

**Dependency Audits:** We ran `pip-audit` and initially detected 32 vulnerabilities. We updated `fastapi` to `0.122.0`, `starlette` to `0.49.3`, and `pip` to `26.2.2`. We ran the `pytest` tests to ensure that these updates did not break the application (**23 tests passed**).

- **Justified risk:** `pip-audit` flagged `pytest 8.3.4`. We accepted this risk because `pytest` was development-only and did not appear in production. Upgrading broke the async testing plugin.
- **Frontend (`npm audit`):** Six moderate-severity vulnerabilities were discovered in the `minimatch` package, linked to a denial-of-service vulnerability. We documented that the vulnerability existed within ESLint, a development-only code-linting tool, and could not be reached through the live application.

**Dynamic Scan of the Running Application (OWASP ZAP):**

We performed an automated ZAP scan on the live application, focusing on both the React frontend (`http://localhost:5173`) and the FastAPI backend (`http://127.0.0.1:8000/docs`).

- **Backend findings:** ZAP detected that the `/docs` endpoint was missing Content Security Policy headers and used cross-domain script inclusion. These findings came from the third-party Swagger UI resources loaded from a CDN. The actual API routes (`/api/v1/predict` and `/api/v1/health`) remained protected by the custom security-header middleware.
- **Frontend findings:** ZAP flagged the Vite development server (`localhost:5173`) for missing anti-clickjacking headers and Subresource Integrity. These were documented as local-development-server findings. In production, the compiled React files must be served by a production web server configured to inject the deployment security headers.

**Malicious Request Testing (`curl`):**

- **CORS attack:** We sent an `OPTIONS` request containing a malicious `Origin` header (`https://group8.attack`). The server returned `400 Bad Request` and `Disallowed CORS Origin`.
- **Payload overflow:** We sent a 20,000-character payload to `/api/v1/predict`. The server rejected it with `413 Request Entity Too Large` and a clean JSON error without exposing a stack trace.
- **Header inspection:** `curl -I` verified that `X-Frame-Options: DENY` and `X-Content-Type-Options: nosniff` were present on responses.

**Cost of the defence:**

The defence had a low runtime cost. Security headers added only a small amount to each HTTP response. Tight CORS configuration created a minor development cost because each future frontend or mobile application must be explicitly allow-listed in `.env`. Pinning dependencies also requires manual review and updates. The team accepted this configuration work to reduce unauthorised cross-origin access and unexpected dependency changes.

**API documentation (`/docs`):**

The FastAPI Swagger UI included endpoint descriptions, summaries and error response models. Pydantic models used `json_schema_extra` to provide example requests and responses.

## Final-state note

The final integration subsequently upgraded FastAPI and Starlette again, remediated the dependency findings, added a restricted documentation CSP, and expanded the backend test suite. Therefore this file is historical before/attack evidence, while the main README contains the final-state results.
