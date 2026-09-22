// find-dup-key.cjs — visit each page, catch each_key_duplicate with URL context
const { chromium } = require('@playwright/test');
const BASE = 'http://localhost:5188';
const PAGES = ['/', '/login', '/dashboard', '/products', '/chat', '/costing', '/settings', '/analytics', '/tasks'];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  let current = '';
  page.on('pageerror', e => {
    const s = String(e);
    if (s.includes('each_key') || s.includes('classList')) {
      console.log(`[${current}] ${s.split('\n').slice(0, 4).join(' | ')}`);
    }
  });
  page.on('console', m => {
    if (m.type() === 'error' && (m.text().includes('each_key') || m.text().includes('classList'))) {
      console.log(`[${current}] CONSOLE: ${m.text().slice(0, 300)}`);
    }
  });

  // login once
  await page.goto(BASE + '/login', { waitUntil: 'networkidle' });
  await page.fill('input[type="email"]', 'admin@mauekspor.example');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await page.waitForURL(u => !String(u).includes('/login'), { timeout: 15000 }).catch(() => {});

  for (const p of PAGES) {
    current = p;
    await page.goto(BASE + p, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(1200);
  }
  console.log('done');
  await browser.close();
})();
