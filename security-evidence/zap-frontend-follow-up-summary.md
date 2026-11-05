# OWASP ZAP frontend follow-up scan

## Scope

- Date: 6 November 2026
- Target: `http://localhost:5173`
- Application: React/Vite local development server
- Scan policy: ZAP Dev Standard
- Traditional spider: enabled
- Modern spider: Client Spider with Chrome Headless
- Session isolation: new ZAP session containing only the frontend target

## Observed results

The completed frontend-only ZAP alert panel reported:

| Severity | Alert category | Instances |
| --- | --- | ---: |
| High | None | 0 |
| Medium | Content Security Policy (CSP) Header Not Set | 3 |
| Medium | Missing Anti-clickjacking Header | 3 |
| Medium | Subresource Integrity Attribute Missing | 3 |
| Low | X-Content-Type-Options Header Missing | Systemic |
| Informational | Information Disclosure — Suspicious Comments | Alert category |
| Informational | Modern Web Application | 3 |

Overall category counts were **0 high, 3 medium, 1 low and 2 informational**.

## Interpretation

The scan reproduces the frontend categories recorded in the team's earlier scan. The medium and low header findings relate to Vite's local development/hot-reload server. Vite is used to run and mark the source project locally; it is not the production web server for the compiled application.

For deployment, `npm run build` produces `frontend/dist`. A production web server or hosting platform must serve that directory and add:

- a deployment-specific Content Security Policy;
- frame protection through `frame-ancestors` and/or `X-Frame-Options`;
- `X-Content-Type-Options: nosniff`;
- integrity-controlled or self-hosted third-party resources where applicable.

The suspicious-comments alert is a passive heuristic and requires inspection of the exact evidence before treating it as sensitive disclosure. The modern-web-application alert is informational technology identification.

## Limitations

- This scan assesses the Vite development server, not a configured production deployment.
- These findings do not apply to FastAPI responses; the backend has separate security middleware and a separate ZAP summary.
- A ZAP result does not prove that no other vulnerability exists.
- The exported frontend HTML report and alert screenshot should be retained with the final submission evidence.
