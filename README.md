# Plazm Launch-Path Security Audit Report

Standalone 33Labs security review of the Plazm launch path in [`BuildTheTech/BackedFund-Contracts`](https://github.com/BuildTheTech/BackedFund-Contracts), exported from source issues [#29–#45](https://github.com/BuildTheTech/BackedFund-Contracts/issues?q=is%3Aissue+number%3A29..45).

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
- Finding baseline: [`213a6dba2e2641804ed56555d4f6f763dbe95200`](https://github.com/BuildTheTech/BackedFund-Contracts/commit/213a6dba2e2641804ed56555d4f6f763dbe95200)
- Remediation snapshot: [`a4dee324e9206e1ddb249ddb3329db9a0712cfc7`](https://github.com/BuildTheTech/BackedFund-Contracts/commit/a4dee324e9206e1ddb249ddb3329db9a0712cfc7)
- Findings: 17 total — 2 Medium, 11 Low, 4 Informational
- Remediation disposition: 15 Fixed, 2 Partially Mitigated
- Final review date: October 22, 2026

## Verification disclosure

[Contracts CI run 39729240593](https://github.com/BuildTheTech/BackedFund-Contracts/actions/runs/39729240593) ran on the remediation snapshot. Dependency audit, compilation, release-consistency checks, contract-size checks, dead-code checks, type checking, and unit tests passed. Exact production coverage failed after a Node.js heap out-of-memory error; downstream deployment replay and Base fork/end-to-end jobs were skipped. The report preserves this limitation and does not claim clean full CI or verified deployment state.

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

The generator reads `sources/issues.json`, uses the canonical files under `assets/`, and writes the release outputs under `reports/` plus the checksum manifest at the repository root.

## Release checksums

- PDF: `0905ef013fec957af23c95ccc29e5cba2d849a4c9724bcf822135dc9cca8f846`
- Markdown: `e2e402f6ffa57156a3fd6deafe2816180937a70f04620d4970b81bb854b34d38`
- JSON: `cf5fe5fb634b7f045f8ad8399cea5ac2f62aa49209695ecee5e3f6106d73ff4a`
- HTML: `63388ee4e53366573bee2573224848f22ba5bb74271446b2340708d26909d693`
