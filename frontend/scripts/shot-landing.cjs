// shot-landing.cjs — screenshot updated landing (light+dark)
const { chromium } = require('@playwright/test');
(async () => {
  const browser = await chromium.launch({ headless: true });
  for (const theme of ['light', 'dark']) {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await ctx.newPage();
    await page.addInitScript(t => localStorage.setItem('mauekspor-theme', t), theme);
    await page.goto('http://localhost:5188/', { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(1800);
    // scroll to stats + EUDR area
    await page.evaluate(() => window.scrollTo(0, 700));
    await page.waitForTimeout(800);
    await page.screenshot({ path: `/tmp/ui-audit/landing-stats-${theme}.png` });
    await ctx.close();
  }
  await browser.close();
  console.log('done');
})();
