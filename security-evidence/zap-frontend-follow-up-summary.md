# OWASP ZAP frontend follow-up scan

## Scope

- Final rescan date: 6 November 2026
- Target: `http://localhost:5173`
- Application: compiled React/Vite build served with `npm run preview`
- Scan policy: ZAP Dev Standard
- Traditional spider: enabled
- Client Spider: Chrome Headless
- Session isolation: new ZAP session containing only the frontend target

## Final observed results

The final frontend ZAP alert panel reported:

| Severity | Alert category | Instances |
| --- | --- | ---: |
| High | None | 0 |
| Medium | CSP `style-src unsafe-inline` | 3 |
| Low | Timestamp Disclosure — Unix | 1 category |
| Informational | Information Disclosure — Suspicious Comments | 1 category |
| Informational | Modern Web Application | 3 |

Overall category counts were **0 high, 1 medium, 1 low and 2 informational**.

## Remediation and interpretation

The earlier frontend scan reported missing CSP, missing anti-clickjacking protection, missing Subresource Integrity metadata and missing `X-Content-Type-Options`. The compiled preview now sends:

- a restrictive Content Security Policy;
- `X-Frame-Options: DENY` and `frame-ancestors 'none'`;
- `X-Content-Type-Options: nosniff`;
- a restrictive referrer policy and permissions policy.

The external Google Fonts stylesheet was removed and replaced with local system-font stacks, eliminating its SRI finding. The final rescan no longer reported missing CSP, anti-clickjacking, SRI or MIME-sniffing protection.

The remaining medium alert is a documented Material UI trade-off. Material UI injects presentation styles at runtime, so `style-src 'unsafe-inline'` is retained while scripts remain restricted to same-origin and the configured nonce.

The low-confidence timestamp alert matched the fixed value `1540483477` inside the compiled JavaScript bundle, representing 26 October 2018. It is not current server time, user data, a session value or application telemetry.

The suspicious-comments heuristic matched the word `select` inside minified selector-processing code. It did not expose a developer comment, database query, credential, path or secret. The Modern Web Application finding is informational technology identification.

## Limitations

- These headers are supplied by the configured Vite preview server for local marking. A real deployment must reproduce them at its production web server or hosting platform.
- The inline-style allowance is a deliberate compatibility trade-off and does not permit inline JavaScript.
- Passive-scan false positives were manually inspected rather than silently ignored.
- A ZAP result does not prove that no other vulnerability exists.
- The final alert screenshot should be retained with the submission evidence.
