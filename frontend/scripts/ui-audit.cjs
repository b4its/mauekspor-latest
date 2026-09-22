// scripts/ui-audit.cjs — Visual UI audit: screenshots light+dark, contrast analysis
const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const BASE = process.env.AUDIT_BASE_URL || 'http://localhost:5188';
const OUT = '/tmp/ui-audit';

const PAGES = [
  { route: '/', name: 'landing' },
  { route: '/login', name: 'login' },
  { route: '/dashboard', name: 'dashboard' },
  { route: '/products', name: 'products' },
  { route: '/chat', name: 'chat' },
  { route: '/costing', name: 'costing' },
  { route: '/settings', name: 'settings' },
];

// WCAG relative luminance + contrast ratio
function lum(hex) {
  hex = hex.replace('#', '');
  if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
  const [r, g, b] = [0, 2, 4].map(i => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map(c => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function ratio(fg, bg) {
  const [a, b] = [lum(fg), lum(bg)].sort((x, y) => y - x);
  return ((a + 0.05) / (b + 0.05)).toFixed(2);
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });

  for (const theme of ['light', 'dark']) {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await ctx.newPage();

    // Collect console errors (bugs!)
    const consoleErrors = [];
    page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text().slice(0, 150)); });
    page.on('pageerror', e => consoleErrors.push('PAGEERROR: ' + String(e).slice(0, 150)));

    // Force theme before load
    await page.addInitScript(t => {
      try { localStorage.setItem('mauekspor-theme', t); } catch (e) {}
      document.documentElement.classList.add(t);
    }, theme);

    console.log(`\n═══ THEME: ${theme} ═══`);
    const findings = [];

    for (const { route, name } of PAGES) {
      try {
        if (['dashboard', 'products', 'chat', 'costing', 'settings'].includes(name)) {
          // login first (once per theme) — handled below via storage
        }
        await page.goto(BASE + route, { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(1200);

        // If redirected to login and we need auth, do login once
        if (page.url().includes('/login') && route !== '/login' && route !== '/') {
          await page.fill('input[type="email"]', 'admin@mauekspor.example');
          await page.fill('input[type="password"]', 'admin123');
          await page.click('button[type="submit"]');
          await page.waitForURL(u => !String(u).includes('/login'), { timeout: 15000 }).catch(() => {});
          await page.goto(BASE + route, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
          await page.waitForTimeout(1000);
        }

        await page.screenshot({ path: path.join(OUT, `${theme}-${name}.png`), fullPage: false });

        // Extract computed colors of key text elements for contrast analysis
        const samples = await page.evaluate(() => {
          // Composite rgba bg over ancestor opaque bg (alpha-aware)
          function bgOf(el) {
            let n = el;
            let r = 255, g = 255, b = 255; // fallback white
            const stack = [];
            while (n && n !== document.documentElement) {
              const bg = getComputedStyle(n).backgroundColor;
              const m = bg && bg.match(/rgba?\(([\d.]+), ([\d.]+), ([\d.]+)(?:, ([\d.]+))?\)/);
              if (m && parseFloat(m[4] ?? '1') > 0) {
                stack.push({ r: +m[1], g: +m[2], b: +m[3], a: parseFloat(m[4] ?? '1') });
                if ((m[4] ?? '1') === '1') break; // opaque — stop
              }
              n = n.parentElement;
            }
            // composite from outermost inward
            for (let i = stack.length - 1; i >= 0; i--) {
              const { r: cr, g: cg, b: cb, a } = stack[i];
              r = cr * a + r * (1 - a);
              g = cg * a + g * (1 - a);
              b = cb * a + b * (1 - a);
            }
            return `rgb(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)})`;
          }
          const pick = (sel, label) => {
            const el = document.querySelector(sel);
            if (!el) return null;
            const s = getComputedStyle(el);
            return {
              label, sel,
              color: s.color, bg: bgOf(el),
              fontSize: s.fontSize, fontWeight: s.fontWeight,
              text: (el.textContent || '').trim().slice(0, 40),
            };
          };
          return [
            pick('h1', 'H1 heading'),
            pick('h2', 'H2 heading'),
            pick('p', 'Paragraph'),
            pick('button', 'Button'),
            pick('a', 'Link'),
            pick('[data-slot="card-title"]', 'Card title'),
            pick('[data-slot="card-description"]', 'Card description'),
            pick('td, [data-slot="table-cell"]', 'Table cell'),
            pick('.text-muted-foreground', 'Muted text'),
            pick('input', 'Input text'),
            pick('label', 'Label'),
          ].filter(Boolean);
        });

        findings.push({ page: name, samples, consoleErrors: [...consoleErrors] });
        consoleErrors.length = 0;
      } catch (e) {
        findings.push({ page: name, error: String(e).slice(0, 120), consoleErrors: [...consoleErrors] });
        consoleErrors.length = 0;
      }
    }

    // Contrast analysis
    console.log(`\n─── Contrast analysis (${theme}) ───`);
    for (const f of findings) {
      if (f.error) { console.log(`  [${f.page}] ERROR: ${f.error}`); continue; }
      for (const s of f.samples) {
        const fg = s.color.match(/\d+/g)?.slice(0, 3).map(Number);
        const bg = s.bg.match(/\d+/g)?.slice(0, 3).map(Number);
        if (!fg || !bg) continue;
        const toHex = c => '#' + c.map(v => v.toString(16).padStart(2, '0')).join('');
        const r = ratio(toHex(fg), toHex(bg));
        const flag = r < 4.5 ? ' ❌ FAIL AA' : (r < 7 ? ' ⚠️  AA only' : ' ✅ AAA');
        console.log(`  [${f.page}] ${s.label.padEnd(18)} ${r}:1 ${flag} (${s.fontSize} ${s.fontWeight}) "${s.text.slice(0, 25)}"`);
      }
    }

    // Console errors = bugs
    const allErrors = findings.flatMap(f => f.consoleErrors || []);
    if (allErrors.length) {
      console.log(`\n─── 🐛 Console errors (${theme}) ───`);
      [...new Set(allErrors)].forEach(e => console.log('  ' + e));
    }

    await ctx.close();
  }

  await browser.close();
  console.log(`\n📁 Screenshots: ${OUT}`);
})();
