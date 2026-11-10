# InsightForge

Dashboard as Code platform built with Python, YAML, Plotly and GitHub Actions.

## Dashboards

- [Overview](https://jmnzcn.github.io/insightforge/) — interactive demonstration using synthetic retail data.
- [Cybersecurity Intelligence](https://jmnzcn.github.io/insightforge/cybersecurity.html) — real public data from CISA KEV, FIRST EPSS and NVD CVSS.

These URLs require GitHub Pages to be configured and a successful deployment.

## Architecture

- `dashboard.yaml` — declarative chart and KPI definitions.
- `scripts/build_dashboard.py` — validation and static bundle generation.
- `pipelines/cybersecurity/build.py` — public API ingestion and enrichment.
- `site/` — interactive static dashboards.
- `tests/` — automated tests.
- `.github/workflows/deploy.yml` — validate and deploy on pushes to main or manual dispatch.
- `.github/workflows/cybersecurity.yml` — scheduled cybersecurity refresh.

## Local development

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/build_dashboard.py
python pipelines/cybersecurity/build.py
python -m http.server 8000 -d site
```

Visit http://localhost:8000 and http://localhost:8000/cybersecurity.html.

## Deployment

In repository **Settings → Pages**, choose **GitHub Actions** as the deployment source. GitHub Actions runs tests, downloads public cyber data, builds the site and deploys to Pages.

## Roadmap

Independent data pipelines for GitHub engineering activity, World Bank economic indicators and open-source AI trends, all feeding the same platform.
