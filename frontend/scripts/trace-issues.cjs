// trace-issues.cjs — find which page throws classList error & which API 403s
const { chromium } = require('@playwright/test');
const BASE = 'http://localhost:5188';
const PAGES = ['/', '/login', '/dashboard', '/products', '/chat', '/costing', '/settings', '/compliance', '/analytics', '/tasks', '/shipments'];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  let cur = '';

  page.on('pageerror', e => {
    const s = String(e);
    if (s.includes('classList')) console.log(`[${cur}] PAGEERROR classList:\n${s.split('\n').slice(0, 8).join('\n')}`);
  });
  page.on('response', r => {
    if (r.status() === 403) console.log(`[${cur}] 403 → ${r.url()}`);
    if (r.status() >= 500) console.log(`[${cur}] ${r.status()} → ${r.url()}`);
  });

  // login once
  await page.goto(BASE + '/login', { waitUntil: 'networkidle' });
  await page.fill('input[type="email"]', 'admin@mauekspor.example');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await page.waitForURL(u => !String(u).includes('/login'), { timeout: 15000 }).catch(() => {});

  for (const p of PAGES) {
    cur = p;
    await page.goto(BASE + p, { waitUntil: 'networkidle', timeout: 30000 }).catch(e => console.log(`[${p}] nav error: ${String(e).slice(0, 80)}`));
    await page.waitForTimeout(1200);
  }
  console.log('done');
  await browser.close();
})();
