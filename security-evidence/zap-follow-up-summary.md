# OWASP ZAP backend follow-up scan

## Scope

- Final rescan date: 6 November 2026
- Target: `http://127.0.0.1:8000/docs`
- Scan policy: ZAP Dev Standard
- Traditional spider: enabled
- Application state: FastAPI running locally with security-header middleware, a restricted documentation CSP, a same-origin Swagger initialiser and integrity metadata on the pinned Swagger assets

This result is compared with the earlier team scan recovered in [`recovered-original-security-results.md`](./recovered-original-security-results.md).

## Final observed results

The clean follow-up ZAP session reported:

| Severity | Alert categories |
| --- | --- |
| High | 0 |
| Medium | 1 — CSP `style-src unsafe-inline` |
| Low | 0 |
| Informational | 1 — Modern Web Application |

## Before-and-after interpretation

The original scan reported that the Swagger documentation had no CSP and loaded external resources without integrity protection. An intermediate follow-up reported two medium categories and one low category: inline Swagger styles, two missing Subresource Integrity attributes, and cross-domain JavaScript inclusion.

The submitted documentation response now:

- sends a restrictive CSP;
- blocks inline JavaScript and loads its initialiser from same-origin `/docs-init.js`;
- pins Swagger UI to version `5.17.14`;
- supplies verified SHA-384 `integrity` metadata and `crossorigin="anonymous"` for both Swagger CSS and JavaScript;
- sends frame, MIME-sniffing, referrer, permissions and HSTS headers.

In the final rescan, both SRI findings and the cross-domain JavaScript warning were no longer reported.

The remaining medium alert is confined to the documentation interface: Swagger UI uses runtime inline presentation styles. The policy still restricts scripts to same-origin and the pinned, integrity-checked jsDelivr asset. Normal JSON API responses use the stricter `default-src 'none'` policy. Removing inline styles would require replacing or substantially modifying Swagger UI and provides little additional protection for this local documentation page.

The Modern Web Application alert is informational technology identification rather than an exploit.

## Limitations

- This scan does not prove that the application has no vulnerabilities.
- The residual inline-style allowance applies to `/docs`, not prediction API JSON responses.
- The scan does not measure the denial-of-service or detection-evasion defences; those have separate reproducible experiments.
- The final alert screenshot should be retained with the submission evidence.
