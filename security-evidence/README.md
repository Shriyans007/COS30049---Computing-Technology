# Dependency and configuration evidence

All commands below were run locally on 5 November 2026. Counts are recorded from the command output rather than inferred from package versions.

## Dependency audit before remediation

`python -m pip_audit -r backend/requirements.txt` reported 10 advisory entries, all against `starlette==0.49.3`. The listed fixes required a Starlette release that the old FastAPI pin did not accept.

`npm audit --json` in `frontend/` reported 6 vulnerable packages: 1 critical and 5 moderate. The direct affected tools were Vitest and ESLint; transitive findings included `@vitest/mocker`, `minimatch` and ESLint configuration packages. They are development tools, but were still remediated because they execute on contributor machines and CI.

## Remediation

- Upgraded FastAPI from 0.122.0 to 0.162.0 and Starlette from 0.49.3 to 1.10.0 together.
- Upgraded Vitest from 4.0.6 to 4.1.12.
- Selected compatible ESLint and `@eslint/js` 9.39.5 versions instead of the affected 10.x combination.
- Removed version ranges so `npm ci` and pip install the reviewed versions.
- Separated production Python packages from test/experiment-only packages.
- Reran backend tests, frontend tests, lint and production build.

## Audit after remediation

Commands:

```powershell
python -m pip_audit -r backend\requirements.txt
Set-Location frontend
npm audit --json
```

Results:

```text
pip-audit: No known vulnerabilities found
npm audit: 0 total vulnerabilities
```

The npm result covered 434 dependencies (91 production and 344 development, plus optional/peer classifications reported by npm). An audit is a point-in-time check, not a guarantee that no vulnerability exists. It should be repeated immediately before submission and deployment.

## Configuration attack checks

Automated backend tests bypass the frontend and verify:

- an untrusted CORS preflight receives `400 CORS_ORIGIN_DENIED` in the shared JSON error format;
- an oversized body receives `413` before model inference;
- a non-JSON prediction receives `415`;
- expected and unexpected errors contain no traceback or local model path;
- security headers exist on successful and early-error responses;
- wildcard CORS and an unprotected non-experiment configuration fail startup.

A team member had already run OWASP ZAP against the live local frontend and backend during the earlier implementation. That scan reported Swagger documentation CSP/cross-domain-resource findings and development-server anti-clickjacking/SRI findings. The original ZAP summary, malicious `curl` checks, dependency results and defence-cost explanation have been recovered in [`recovered-original-security-results.md`](./recovered-original-security-results.md).

The recovered file is retained as historical attack evidence. Later dependency and security-header changes supersede some of its package versions and documentation findings; the main README reports the final submitted configuration.

A backend follow-up scan was then completed after documentation hardening. Its observed severity counts, remaining findings, before/after interpretation and limitations are recorded in [`zap-follow-up-summary.md`](./zap-follow-up-summary.md).

A separate frontend-only scan reproduced the Vite development-server findings from the earlier team scan. Its isolated counts and deployment interpretation are recorded in [`zap-frontend-follow-up-summary.md`](./zap-frontend-follow-up-summary.md).
