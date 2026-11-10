# Cybersecurity Intelligence pipeline

Public sources:
- CISA Known Exploited Vulnerabilities (KEV): https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- FIRST EPSS API: https://api.first.org/data/v1/epss
- NVD CVE API: https://nvd.nist.gov/developers/vulnerabilities

The pipeline downloads a bounded sample of the most recently added CISA KEV entries (up to 60), enriches each with EPSS probability, and enriches a smaller bounded sample (up to 10) with NVD CVSS metrics. No API keys are required. Missing enrichments are represented as null, not zero. It builds a static dashboard JSON bundle.

## Local

```bash
python pipelines/cybersecurity/build.py
python -m http.server 8000 -d site
```

Then open `http://localhost:8000/cybersecurity.html`.

## Operational limits

The CISA feed is a catalog of *known exploited* vulnerabilities, not all CVEs. EPSS is a probability estimate, not a guarantee. NVD CVSS describes severity, not actual organizational exposure. API requests may fail or rate-limit; the pipeline fails rather than publishing misleading empty data. The sample is intentionally bounded for public CI.
