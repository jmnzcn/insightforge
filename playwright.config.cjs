const { defineConfig } = require('@playwright/test');
module.exports = defineConfig({
  testDir: './e2e',
  timeout: 45000,
  expect: { timeout: 12000 },
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['list'], ['html', { outputFolder: 'playwright-report', open: 'never' }]] : 'list',
  use: { headless: true, trace: 'retain-on-failure', screenshot: 'on', video: 'retain-on-failure' },
  projects: [
    { name: 'local', use: { baseURL: 'http://127.0.0.1:8000', browserName: 'chromium' }, testMatch: '**/dashboard.spec.cjs' },
    { name: 'live', use: { baseURL: 'https://jmnzcn.github.io/insightforge', browserName: 'chromium' }, testMatch: '**/dashboard.spec.cjs' },
  ],
});
