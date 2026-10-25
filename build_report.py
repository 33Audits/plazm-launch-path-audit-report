#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import markdown
import pymupdf
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent
ISSUES_PATH = ROOT / "sources" / "issues-refresh.json"
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)
OUT_MD = REPORTS / "plazm-launch-path-security-audit-report.md"
OUT_JSON = REPORTS / "plazm-launch-path-security-audit-report.json"
OUT_HTML = REPORTS / "plazm-launch-path-security-audit-report.html"
OUT_PDF = REPORTS / "plazm-launch-path-security-audit-report.pdf"

REPO = "BuildTheTech/BackedFund-Contracts"
REPO_URL = f"https://github.com/{REPO}"
AUDITED_SHA = "a4dee324e9206e1ddb249ddb3329db9a0712cfc7"
REMEDIATION_SHA = "2d210dbfe293a00122de726848c47e4472733bfb"
CI_URL = "https://github.com/BuildTheTech/BackedFund-Contracts/actions/runs/40078929418"
REPORT_DATE = "October 24, 2026"
AUTHORS = [
    {"name": "0x23r0", "role": "Security Researcher", "url": "https://github.com/0x23r0"},
    {"name": "Favour Aniogor", "role": "Security Researcher", "url": "https://github.com/PhantomOz"},
]
PARTIAL = {36, 46}

SEVERITY_ORDER = {"High": 0, "Medium": 1, "Low": 2, "Informational": 3}
SEVERITY_PREFIX = {"High": "H", "Medium": "M", "Low": "L", "Informational": "I"}


def normalize_fences(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    open_fence = False
    for line in lines:
        if not open_fence and re.match(r"^```[^`\s]+:[^`]*$", line.strip()):
            meta = line.strip()[3:]
            lang = "solidity" if ".sol" in meta else "text"
            out.extend([f"```{lang}", f"// Source: {meta}"])
            open_fence = True
        elif line.strip().startswith("```"):
            out.append(line)
            open_fence = not open_fence
        else:
            out.append(line)
    return "\n".join(out).strip()


def split_sections(body: str) -> tuple[str, dict[str, str]]:
    body = normalize_fences(body)
    matches = list(re.finditer(r"^#{2,4}\s+(Description|Impact|Proof of concept|Proof of Concept|Recommendation|Status)\s*$", body, re.M | re.I))
    if not matches:
        return body.strip(), {}
    preface = body[: matches[0].start()].strip()
    sections: dict[str, str] = {}
    for i, match in enumerate(matches):
        name = match.group(1).lower()
        key = {
            "description": "Description",
            "impact": "Impact",
            "proof of concept": "Proof of Concept",
            "recommendation": "Recommendation",
            "status": "Status",
        }[name]
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[key] = body[match.end() : end].strip()
    return preface, sections


def latest_review(issue: dict) -> dict:
    preferred = [c for c in issue["comments"] if c["author"] == "PhantomOz"]
    return (preferred or issue["comments"])[-1]


issues = sorted(json.loads(ISSUES_PATH.read_text()), key=lambda x: x["number"])
assert [x["number"] for x in issues] == list(range(29, 50))

# Assign report-local IDs sequentially inside each severity group while retaining source IDs.
by_severity: dict[str, list[dict]] = defaultdict(list)
for issue in issues:
    m = re.match(r"^\[([HMLI])-\d+\]\s*(.+)$", issue["title"])
    assert m, issue["title"]
    sev = {"H": "High", "M": "Medium", "L": "Low", "I": "Informational"}[m.group(1)]
    issue["clean_title"] = m.group(2)
    issue["source_finding_id"] = re.match(r"^\[([^]]+)\]", issue["title"]).group(1)
    issue["severity"] = sev
    by_severity[sev].append(issue)

findings: list[dict] = []
for sev in sorted(by_severity, key=lambda x: SEVERITY_ORDER[x]):
    for idx, issue in enumerate(by_severity[sev], 1):
        report_id = f"{SEVERITY_PREFIX[sev]}-{idx:02d}"
        preface, sections = split_sections(issue["body"])
        review = latest_review(issue)
        status = "Partially Mitigated" if issue["number"] in PARTIAL else "Fixed"
        poc = sections.get("Proof of Concept") or "No standalone proof-of-concept section was supplied in the source issue. The source issue documents the code trace and validation evidence used for review."
        findings.append({
            "id": report_id,
            "source_finding_id": issue["source_finding_id"],
            "source_issue": issue["number"],
            "title": issue["clean_title"],
            "severity": sev,
            "status": status,
            "issue_state": issue["state"],
            "issue_url": issue["url"],
            "created_at": issue["created_at"],
            "updated_at": issue["updated_at"],
            "audited_sha": AUDITED_SHA,
            "remediation_sha": REMEDIATION_SHA,
            "description": ((preface + "\n\n") if preface else "") + sections.get("Description", "Not supplied in the source issue."),
            "impact": sections.get("Impact", "Not supplied in the source issue."),
            "proof_of_concept": poc,
            "recommendation": sections.get("Recommendation", "Not supplied in the source issue."),
            "status_note": review["body"].strip(),
            "status_evidence_url": review["url"],
            "comments": issue["comments"],
            "issue_body_sha256": hashlib.sha256(issue["body"].encode()).hexdigest(),
        })

severity_counts = Counter(f["severity"] for f in findings)
status_counts = Counter(f["status"] for f in findings)
assert severity_counts == {"Medium": 2, "Low": 15, "Informational": 4}
assert status_counts == {"Fixed": 19, "Partially Mitigated": 2}

front = f"""# Plazm Launch-Path Security Audit Report

## Introduction

33Labs performed a focused review of the Plazm launch path implemented in [`{REPO}`]({REPO_URL}). This report is a separate export of GitHub issues [#29]({REPO_URL}/issues/29) through [#49]({REPO_URL}/issues/49), covering launch settlement, recurring liquidity drips, route capacity, treasury reinvestment, OTC capacity and rounding, V4 accounting bounds, guardian rotation, sale timing, and creator-supply accounting.

The review identified **21 findings**: **2 Medium**, **15 Low**, and **4 Informational**. Against remediation snapshot [`{REMEDIATION_SHA}`]({REPO_URL}/commit/{REMEDIATION_SHA}), **19 findings are Fixed** and **2 are Partially Mitigated** with documented residual conditions.

## Audit Team

| Auditor | Role |
|---|---|
| [0x23r0 ↗](https://github.com/0x23r0) | Security Researcher |
| [Favour Aniogor ↗](https://github.com/PhantomOz) | Security Researcher |

## Disclaimer

This report is a point-in-time security assessment, not a guarantee that the reviewed system is free of vulnerabilities. Findings and remediation dispositions are based on the scoped repository, source issue ledger, reviewer comments, and evidence available at the stated snapshots. Deployment configuration, operational procedures, third-party dependencies, and code changed after the remediation snapshot may introduce additional risk.

## About 33Labs

33Labs is an independent smart contract security research and development group with six years of experience and over 40 completed audits. We specialize in building and auditing Solidity, Rust, Move, and DeFi systems. Learn more at [33labs.ai](https://33labs.ai) or follow us on X [@33labs_](https://x.com/33labs_).

## About the Plazm Launch Path

The reviewed path coordinates permissionless launches whose raised assets are converted or settled through Plazm and related routes, then deployed into locked liquidity and recurring liquidity-drip programs. The scope also includes adjacent treasury reinvestment and project-support paths where the same route-capacity, pricing, lifecycle, and delta-accounting assumptions apply.

## Audit Scope

- **Repository:** [`{REPO}`]({REPO_URL})
- **Branch:** `main`
- **Finding baseline:** [`{AUDITED_SHA}`]({REPO_URL}/commit/{AUDITED_SHA})
- **Remediation snapshot:** [`{REMEDIATION_SHA}`]({REPO_URL}/commit/{REMEDIATION_SHA})
- **Source issues:** [#29–#49]({REPO_URL}/issues?q=is%3Aissue+number%3A29..49)
- **Issue creation window:** October 19–22, 2026
- **Final review date:** {REPORT_DATE}

The report is limited to the behavior documented by those 21 issues and their directly related launch-path code. It does not reopen or duplicate issues #1–#28 from the broader BackedFund report.

## Methodology

The review combined issue-ledger reconstruction, manual source-path analysis, exploit and liveness reasoning, delta/accounting review, route-capacity analysis, lifecycle checks, and remediation reconciliation. Each disposition was checked against the latest reviewer evidence at `{REMEDIATION_SHA[:8]}` rather than inferred from GitHub issue state.

## Verification Evidence and Limits

[Contracts CI run 40078929418]({CI_URL}) executed on the exact remediation snapshot. The contracts job failed only at exact production coverage; the Base Plazm fork and Base protocol end-to-end jobs were skipped. Issue-level round-five comments record targeted regressions passing for the updated findings, including Base-fork verification for the reinvestment sandwich case. This report distinguishes those recorded targeted results from an independently rerun full suite and does not claim clean full CI or verified deployment state.

## Severity Classification

- **Medium:** credible material loss, prolonged liveness failure, or protocol malfunction under realistic but constrained preconditions.
- **Low:** limited-impact, edge-case, hardening, or constrained liveness issue.
- **Informational:** design, integration, or operational observation with low direct exploit impact.

## Findings Summary

| ID | Finding | Severity | Status | Source |
|---|---|---|---|---|
"""

summary_rows = []
for f in findings:
    summary_rows.append(f"| {f['id']} | {f['title']} | {f['severity']} | {f['status']} | [#{f['source_issue']} ↗]({f['issue_url']}) |")

finding_sections = []
for f in findings:
    status_intro = "**Partially Mitigated.**" if f["status"] == "Partially Mitigated" else "**Fixed.**"
    finding_sections.append(f"""# [{f['id']}] {f['title']}

**Severity:** {f['severity']}  
**Source finding:** `{f['source_finding_id']}`  
**Source issue:** [#{f['source_issue']} ↗]({f['issue_url']})  
**Audited baseline:** [`{AUDITED_SHA[:8]}`]({REPO_URL}/commit/{AUDITED_SHA})  
**Remediation snapshot:** [`{REMEDIATION_SHA[:8]}`]({REPO_URL}/commit/{REMEDIATION_SHA})

## Description

{f['description']}

## Impact

{f['impact']}

## Proof of Concept

{f['proof_of_concept']}

## Recommendation

{f['recommendation']}

## Status

{status_intro} [Latest reviewer evidence ↗]({f['status_evidence_url']})

{f['status_note']}
""")

conclusion = f"""# Conclusion

The Plazm launch-path review identified **21 findings**: **2 Medium**, **15 Low**, and **4 Informational**. At remediation snapshot [`{REMEDIATION_SHA}`]({REPO_URL}/commit/{REMEDIATION_SHA}), **19 findings are Fixed** and **2 are Partially Mitigated**.

The two residual items are:

- **L-06 / source L-22 (#36):** the project-token side is bounded by the new maximum total-supply rule, while the counter-asset side still relies on WETH, PLAZM, and approved Build-on-Asset counters remaining below the V4 `int128` amount limit; that requirement is documented but not enforced on-chain.
- **L-12 / source L-28 (#46):** minimum-size asks, accounting, and expired-order matching are fixed, but an attacker can still create 128 short-lived minimum-size asks to exhaust the scan bound and temporarily deny OTC routing until someone cancels them. The remaining impact is low and the DEX leg continues to work.

Issue #49's original partial-OTC slot mismatch is fixed at the remediation snapshot. Its latest review records a separate residual condition in which a maker can withdraw OTC inventory after settlement planning; that condition relies on the spare slot or `extendSettlementWindow` and is retained in the finding evidence rather than misclassified as the original defect.

The exact-snapshot contracts CI job failed at exact production coverage, while downstream fork/end-to-end jobs were skipped. Targeted issue-level regressions passed, including Base-fork verification for the reinvestment sandwich case. Those limitations remain part of the release risk and should not be interpreted as a clean full-CI attestation.
"""

md = front + "\n".join(summary_rows) + "\n\n" + "\n\n".join(finding_sections) + "\n\n" + conclusion
OUT_MD.write_text(md)

structured = {
    "report": {
        "title": "Plazm Launch-Path Security Audit Report",
        "organization": "33Labs",
        "client": "BackedFund",
        "protocol": "Plazm launch path",
        "report_date": "2026-10-22",
        "repository": REPO_URL,
        "branch": "main",
        "audited_sha": AUDITED_SHA,
        "remediation_sha": REMEDIATION_SHA,
        "source_issue_range": [29, 49],
        "ci": {"run_url": CI_URL, "contracts_job": "failed at exact production coverage", "coverage": "failed", "downstream_jobs": "skipped", "targeted_issue_regressions": "documented as passing; includes Base-fork verification for #41"},
        "totals": {"findings": 21, "severity": dict(severity_counts), "status": dict(status_counts)},
        "authors": AUTHORS,
    },
    "findings": findings,
}
OUT_JSON.write_text(json.dumps(structured, indent=2, ensure_ascii=False) + "\n")

body = markdown.markdown(md, extensions=["fenced_code", "tables", "toc", "sane_lists"])
css = r"""
@page { size: Letter; margin: .72in .65in .68in; @bottom-center { content: "33Labs • Plazm Launch-Path Security Audit"; color:#7b8794; font-size:8px; } @bottom-right { content: counter(page); color:#7b8794; font-size:8px; } }
@page cover { margin:0; @bottom-center { content:none } @bottom-right { content:none } }
* { box-sizing:border-box; }
body { margin:0; font-family: Inter, Arial, sans-serif; color:#172033; font-size:9.2pt; line-height:1.46; }
.cover { page:cover; page-break-after:always; height:10.98in; width:8.5in; margin:0; padding:.9in; background:linear-gradient(145deg,#08172b 0%,#153558 58%,#0a7a97 100%); color:white; position:relative; overflow:hidden; }
.cover h1 { font-size:39pt; line-height:1.02; margin:2.3in 0 .18in; color:white; border:0; page-break-before:auto; }
.cover h2 { font-size:18pt; color:#c8f2f4; margin:0; font-weight:500; }
h1 { color:#0c2f55; font-size:23pt; line-height:1.08; page-break-before:always; border-bottom:3px solid #1aa6b7; padding-bottom:8px; }
h2 { color:#0d426f; font-size:15pt; margin-top:24px; page-break-after:avoid; }
h3 { color:#0f6a7f; font-size:11.5pt; margin-top:18px; page-break-after:avoid; }
h4 { color:#274c67; font-size:10pt; page-break-after:avoid; }
a { color:#145fc0; text-decoration:underline; }
table { width:100%; border-collapse:collapse; margin:12px 0 18px; font-size:8.15pt; }
thead { display:table-header-group; }
tr { break-inside:avoid; page-break-inside:avoid; }
th { background:#e5e7eb; color:#1f2937; padding:7px; text-align:left; border:1px solid #cbd5e1; }
td { padding:7px; border:1px solid #d8e0e8; vertical-align:top; overflow-wrap:anywhere; }
td:first-child { width:20%; overflow-wrap:normal; word-break:normal; }
tr:nth-child(even) td { background:#f8fafc; }
#findings-summary + table { width:100%; table-layout:fixed; font-size:7.5pt; }
#findings-summary + table th:nth-child(1), #findings-summary + table td:nth-child(1) { width:7%; white-space:nowrap; }
#findings-summary + table th:nth-child(2), #findings-summary + table td:nth-child(2) { width:51%; }
#findings-summary + table th:nth-child(3), #findings-summary + table td:nth-child(3) { width:12%; white-space:nowrap; }
#findings-summary + table th:nth-child(4), #findings-summary + table td:nth-child(4) { width:18%; }
#findings-summary + table th:nth-child(5), #findings-summary + table td:nth-child(5) { width:12%; white-space:nowrap; }
pre { background:#0b1627; color:#e5edf8; border-radius:6px; padding:10px; font-size:7.1pt; line-height:1.34; white-space:pre-wrap; overflow-wrap:anywhere; break-inside:auto; box-decoration-break:clone; }
code { font-family:"DejaVu Sans Mono",monospace; font-size:.88em; }
p code, li code { background:#eef3f7; color:#17324b; padding:1px 3px; border-radius:3px; }
blockquote { border-left:3px solid #1aa6b7; margin-left:0; padding-left:12px; color:#42566a; }
hr { border:0; border-top:1px solid #cbd5e1; margin:22px 0; }
"""
cover = '<section class="cover"><h1>Plazm</h1><h2>Launch-Path Audit Report</h2></section>'
html_doc = f'<!doctype html><html><head><meta charset="utf-8"><title>Plazm Launch-Path Security Audit Report</title><style>{css}</style></head><body>{cover}{body}</body></html>'
OUT_HTML.write_text(html_doc)
HTML(string=html_doc, base_url=str(ROOT)).write_pdf(OUT_PDF)

# Replace the synthetic first page with the exact Recoup-family cover asset.
generated = pymupdf.open(OUT_PDF)
approved_cover = pymupdf.open(ROOT / "assets" / "plazm-launch-path-cover.pdf")
merged = pymupdf.open()
merged.insert_pdf(approved_cover, from_page=0, to_page=0, links=True, annots=True)
merged.insert_pdf(generated, from_page=1, to_page=generated.page_count - 1, links=True, annots=True)
merged.set_metadata({**generated.metadata, "title": "Plazm Launch-Path Security Audit Report", "author": "0x23r0; Favour Aniogor; 33Labs", "subject": "Smart contract security review"})
tmp = ROOT / "plazm-launch-path-security-audit-report.merged.pdf"
merged.save(tmp, garbage=4, deflate=True)
merged.close(); approved_cover.close(); generated.close(); tmp.replace(OUT_PDF)

# Release assertions.
doc = pymupdf.open(OUT_PDF)
pdf_text = "\n".join(page.get_text() for page in doc)
pdf_links = {link.get("uri") for page in doc for link in page.get_links() if link.get("uri")}
assert doc[0].rect == pymupdf.Rect(0, 0, 612, 842.25)
assert doc[0].get_text().strip().splitlines() == ["Plazm", "Launch-Path Audit Report"]
assert all(doc[i].rect == pymupdf.Rect(0, 0, 612, 792) for i in range(1, doc.page_count))
assert "21 findings" in pdf_text and "19 findings are Fixed" in pdf_text and "2 are Partially Mitigated" in pdf_text
assert "0x23r0" in pdf_text and "Favour Aniogor" in pdf_text
assert AUDITED_SHA in pdf_text and REMEDIATION_SHA in pdf_text
for uri in [a["url"] for a in AUTHORS] + ["https://33labs.ai", "https://x.com/33labs_"] + [f["issue_url"] for f in findings]:
    assert uri in pdf_links, f"Missing PDF link annotation: {uri}"
for f in findings:
    assert f"[{f['id']}]" in pdf_text
assert doc.page_count > 20

manifest = {}
for path in [OUT_MD, OUT_HTML, OUT_PDF, OUT_JSON]:
    payload = path.read_bytes()
    manifest[path.name] = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
(ROOT / "SHA256SUMS.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"pages": doc.page_count, "links": len(pdf_links), "severity": dict(severity_counts), "status": dict(status_counts), "artifacts": manifest}, indent=2))
