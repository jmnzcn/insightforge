const { test, expect } = require('@playwright/test');

test('overview dashboard renders KPI cards and interactive charts', async ({ page }) => {
  await page.goto('index.html', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('#title')).toHaveText('InsightForge');
  await expect(page.locator('#kpis .kpi')).toHaveCount(3);
  await expect(page.locator('#charts .chart-card')).toHaveCount(3);
  await expect(page.locator('#charts .js-plotly-plot')).toHaveCount(3);
  const initial = await page.locator('#records').innerText();
  await page.locator('#region').selectOption('North');
  await expect(page.locator('#records')).not.toHaveText(initial);
  await page.locator('#reset').click();
  await expect(page.locator('#records')).toHaveText(initial);
  await page.screenshot({ path: 'test-results/overview.png', fullPage: true });
});

test('cybersecurity dashboard loads public-data bundle and responds to filters', async ({ page, request }) => {
  const response = await request.get('cybersecurity.json');
  expect(response.ok(), 'cybersecurity.json must be publicly served').toBeTruthy();
  const bundle = await response.json();
  expect(bundle.sources.kev).toContain('cisa.gov');
  expect(bundle.sources.epss).toContain('first.org');
  expect(bundle.sources.nvd).toContain('nist.gov');
  expect(bundle.rows.length).toBeGreaterThan(0);
  expect(bundle.rows[0].cve).toMatch(/^CVE-\d{4}-\d{4,}$/);
  expect(bundle.rows.some(r => r.epss !== null)).toBeTruthy();
  await page.goto('cybersecurity.html', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('#kpis .kpi')).toHaveCount(3);
  await expect(page.locator('#vendors.js-plotly-plot')).toBeVisible();
  await expect(page.locator('#epss.js-plotly-plot')).toBeVisible();
  await expect(page.locator('#cves tr').first()).toContainText('CVE');
  const vendorOptions = await page.locator('#vendor option').count();
  expect(vendorOptions).toBeGreaterThan(1);
  const selected = await page.locator('#vendor option').nth(1).getAttribute('value');
  await page.locator('#vendor').selectOption(selected);
  await expect(page.locator('#cves tr').nth(1)).toContainText(selected);
  await page.locator('#reset').click();
  await expect(page.locator('#vendor')).toHaveValue('');
  await page.screenshot({ path: 'test-results/cybersecurity.png', fullPage: true });
});
