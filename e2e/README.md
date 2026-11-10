# Browser verification

Playwright validates **both** generated local HTML and the deployed public GitHub Pages site.

Checks:
- Overview KPI cards and Plotly chart rendering.
- Region filter and reset.
- Public cybersecurity JSON source URLs, nonempty real CVEs, and EPSS enrichment.
- Cyber dashboard KPI cards, charts, vendor filter and reset.
- Full-page screenshots and HTML report uploaded as GitHub Actions artifacts.

Run locally:
```bash
python -m pip install -r requirements.txt
python scripts/build_dashboard.py
python pipelines/cybersecurity/build.py
python -m http.server 8000 -d site
npm install
npx playwright install chromium
npx playwright test --project=local
```

GitHub Actions workflow: **Browser E2E verification**. Manual runs test both local and live; pull requests test local only. Scheduled runs test both. Test reports and screenshots are attached as downloadable workflow artifacts even when tests fail.
