# OWASP ZAP follow-up scan

## Scope

- Date: 5 November 2026
- Target: `http://127.0.0.1:8000/docs`
- Scan policy: ZAP Dev Standard
- Traditional spider: enabled
- Application state: FastAPI backend running locally with the restricted documentation CSP and CSP-compatible external Swagger initialiser

This follow-up is compared with the earlier team scan recovered in [`recovered-original-security-results.md`](./recovered-original-security-results.md).

## Observed results

The completed ZAP alert panel reported:

| Severity | Alert categories |
| --- | --- |
| High | 0 |
| Medium | 2 — CSP `style-src unsafe-inline`; Subresource Integrity Attribute Missing (two resource instances) |
| Low | 1 — Cross-Domain JavaScript Source File Inclusion |
| Informational | 1 — Modern Web Application |

## Before-and-after interpretation

The earlier scan reported a missing CSP on the Swagger documentation. In the follow-up scan, ZAP no longer reported a missing CSP: the documentation now sends a restricted policy. ZAP instead identified the narrower residual issue that Swagger presentation permits inline styles. Inline JavaScript is not permitted; Swagger initialisation is served from the same-origin `/docs-init.js` resource.

The SRI and cross-domain findings relate to the pinned Swagger UI resources loaded from the CSP-allow-listed jsDelivr origin. Pinning and CSP reduce accidental version drift and restrict resource origins, but they do not provide the same integrity guarantee as self-hosting or valid SRI hashes. These findings are therefore documented as residual supply-chain risks rather than dismissed.

The Modern Web Application alert is informational technology identification.

## Limitations

- This follow-up targeted the backend Swagger interface. It does not replace a separate frontend scan.
- ZAP findings do not prove that an application has no vulnerabilities.
- The scan does not measure the denial-of-service defence or detection-evasion defence; those have separate reproducible experiments.
- The exported HTML report and alert screenshot should be retained with the final submission evidence.
