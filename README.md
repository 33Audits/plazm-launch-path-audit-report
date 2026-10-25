# Plazm Launch-Path Security Audit Report

Standalone 33Labs security review of the Plazm launch path in [`BuildTheTech/BackedFund-Contracts`](https://github.com/BuildTheTech/BackedFund-Contracts), refreshed from source issues [#29–#49](https://github.com/BuildTheTech/BackedFund-Contracts/issues?q=is%3Aissue+number%3A29..49) and their latest remediation comments.

This publication is separate from the broader BackedFund report covering issues #1–#28.

## Report

- [PDF](reports/plazm-launch-path-security-audit-report.pdf)
- [Markdown](reports/plazm-launch-path-security-audit-report.md)
- [Structured JSON](reports/plazm-launch-path-security-audit-report.json)
- [HTML render source](reports/plazm-launch-path-security-audit-report.html)
- [Checksums](SHA256SUMS.json)

## Audit team

- [0x23r0](https://github.com/0x23r0) — Security Researcher
- [Favour Aniogor](https://github.com/PhantomOz) — Security Researcher

## Scope and snapshots

- Source repository: [`BuildTheTech/BackedFund-Contracts`](https://github.com/BuildTheTech/BackedFund-Contracts)
- Finding baseline: [`a4dee324e9206e1ddb249ddb3329db9a0712cfc7`](https://github.com/BuildTheTech/BackedFund-Contracts/commit/a4dee324e9206e1ddb249ddb3329db9a0712cfc7)
- Remediation snapshot: [`2d210dbfe293a00122de726848c47e4472733bfb`](https://github.com/BuildTheTech/BackedFund-Contracts/commit/2d210dbfe293a00122de726848c47e4472733bfb)
- Findings: 21 total — 2 Medium, 15 Low, 4 Informational
- Remediation disposition: 21 Fixed
- Final review date: October 25, 2026

## Verification disclosure

All 21 findings carry the client-confirmed `Fixed` disposition. [Contracts CI run 40078929418](https://github.com/BuildTheTech/BackedFund-Contracts/actions/runs/40078929418) ran on the remediation snapshot. The contracts job failed at exact production coverage; Base Plazm fork and Base protocol end-to-end jobs were skipped. Round-five issue comments record targeted regressions passing, including Base-fork verification for the reinvestment sandwich case. The report does not claim clean full CI or verified deployment state.

## Reproducibility

The report uses the established Recoup/33Labs report family:

- Exact 33Labs background and white logo assets
- Embedded `DarkerGrotesque-Bold.ttf` cover typography
- `612 × 842.25` point cover
- `612 × 792` point US Letter body pages
- Linked authors, findings, commits, and source issues

Rebuild from the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python create_cover.py
.venv/bin/python build_report.py
```

The generator reads `sources/issues-refresh.json`, uses the canonical files under `assets/`, and writes the release outputs under `reports/` plus the checksum manifest at the repository root.

## Release checksums

- PDF: `6525a832242e71483e52ec52ccb2ea6863e6010d18155277d342adadeec47109`
- Markdown: `0c1da75bc7eda4b786c96c66c5b441757e64b3c0924b3730b0c090e85213c146`
- JSON: `73d2b7a83b9060af67ea478e523dcfdbd539b25730816d4843c11fa40a526799`
- HTML: `7c1a9b3362a3dd0ed7cca5a9f334600c82b387b41f41554e055602698131bcc8`
