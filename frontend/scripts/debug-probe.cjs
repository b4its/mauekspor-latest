// debug-probe.cjs — precise probes for remaining issues
const { chromium } = require('@playwright/test');
const BASE = 'http://localhost:5188';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();

  page.on('pageerror', e => console.log('PAGEERROR:', String(e).split('\n').slice(0, 6).join(' | ')));
  page.on('console', m => { if (m.type() === 'error') console.log('CONSOLE:', m.text().slice(0, 200)); });

  await page.goto(BASE + '/dashboard', { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(1500);

  // 1. Exact computed colors for breadcrumb + muted elements
  const probe = await page.evaluate(() => {
    const out = [];
    const link = document.querySelector('[data-slot="breadcrumb-link"]');
    if (link) {
      const s = getComputedStyle(link);
      out.push({ el: 'breadcrumb-link', color: s.color, cls: link.className.slice(0, 80) });
    }
    const list = document.querySelector('[data-slot="breadcrumb-list"]');
    if (list) out.push({ el: 'breadcrumb-list', color: getComputedStyle(list).color });
    const muted = document.querySelector('.text-muted-foreground');
    if (muted) out.push({ el: 'muted-first', color: getComputedStyle(muted).color, cls: muted.className.slice(0, 60) });
    out.push({ el: 'html-dark?', dark: document.documentElement.classList.contains('dark') });
    const cssMuted = getComputedStyle(document.documentElement).getPropertyValue('--muted-foreground');
    out.push({ el: '--muted-foreground value', color: cssMuted.trim() });
    return out;
  });
  console.log('=== COLOR PROBE ===');
  probe.forEach(p => console.log(JSON.stringify(p)));

  // 2. Find duplicate each_key_duplicate source
  console.log('\n=== DUPLICATE KEY PROBE (landing) ===');
  await page.goto(BASE + '/', { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(1500);

  await browser.close();
})();
