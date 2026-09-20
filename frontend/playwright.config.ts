import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  // Run tests sequentially – screenshots depend on consistent state
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: 1,
  reporter: [
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['list'],
  ],
  use: {
    baseURL: 'http://localhost:5173',
    // Keep browser state across tests within a describe (shared context)
    trace: 'retain-on-failure',
    screenshot: 'on',            // always save screenshot on failure
    video: 'retain-on-failure',
    viewport: { width: 1440, height: 900 },
    // Generous timeout so slow pages don't fail
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
    // Ignore HTTPS errors (dev server)
    ignoreHTTPSErrors: true,
  },
  timeout: 60_000,
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  outputDir: './test-results/playwright',
});
