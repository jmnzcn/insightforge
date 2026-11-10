"""Build a public-data cyber intelligence dashboard bundle (stdlib only)."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
CISA_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
EPSS_URL = "https://api.first.org/data/v1/epss"
NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
USER_AGENT = "InsightForge/0.2 (public cybersecurity analytics; GitHub jmnzcn/insightforge)"


def get_json(url: str, *, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urlopen(request, timeout=35) as response:
                return json.load(response)
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def normalize_kev(items: list[dict], limit: int = 60) -> list[dict]:
    """Keep recent KEV records with required fields; preserve source semantics."""
    valid = [v for v in items if v.get("cveID") and v.get("dateAdded")]
    valid.sort(key=lambda v: (v["dateAdded"], v["cveID"]), reverse=True)
    result = []
    for v in valid[:limit]:
        result.append({
            "cve": v["cveID"],
            "date_added": v["dateAdded"],
            "vendor": v.get("vendorProject") or "Unknown",
            "product": v.get("product") or "Unknown",
            "name": v.get("vulnerabilityName") or "",
            "ransomware": v.get("knownRansomwareCampaignUse") or "Unknown",
            "epss": None,
            "cvss": None,
        })
    return result


def enrich_epss(rows: list[dict]) -> None:
    if not rows:
        return
    for offset in range(0, len(rows), 30):
        batch = rows[offset:offset + 30]
        params = urlencode({"cve": ",".join(v["cve"] for v in batch)})
        data = get_json(EPSS_URL + "?" + params).get("data", [])
        scores = {v["cve"]: float(v["epss"]) for v in data if v.get("epss") is not None}
        for row in batch:
            row["epss"] = scores.get(row["cve"])


def extract_cvss(cve: dict) -> float | None:
    metrics = cve.get("metrics") or {}
    for key in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        for metric in metrics.get(key, []):
            value = metric.get("cvssData", {}).get("baseScore")
            if value is not None:
                return float(value)
    return None


def enrich_nvd(rows: list[dict], limit: int = 10) -> None:
    for row in rows[:limit]:
        data = get_json(NVD_URL + "?" + urlencode({"cveId": row["cve"]}))
        vulnerabilities = data.get("vulnerabilities", [])
        if vulnerabilities:
            row["cvss"] = extract_cvss(vulnerabilities[0].get("cve", {}))
        time.sleep(0.7)


def build_bundle(kev_data: dict, *, with_nvd: bool = True) -> dict:
    entries = kev_data.get("vulnerabilities")
    if not isinstance(entries, list):
        raise ValueError("CISA KEV feed missing vulnerabilities array")
    rows = normalize_kev(entries)
    if not rows:
        raise ValueError("No valid KEV records")
    enrich_epss(rows)
    if with_nvd:
        enrich_nvd(rows)
    return {
        "title": "Cybersecurity Intelligence",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": {"kev": CISA_URL, "epss": EPSS_URL, "nvd": NVD_URL},
        "sampling": {"kev_limit": 60, "nvd_limit": 10},
        "rows": rows,
    }


def main() -> None:
    kev_data = get_json(CISA_URL)
    bundle = build_bundle(kev_data)
    output = ROOT / "site" / "cybersecurity.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Built {len(bundle['rows'])} real KEV records -> {output}")


if __name__ == "__main__":
    main()
