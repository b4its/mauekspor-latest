import { test, expect, type Page, type BrowserContext } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// ─── Credentials from seed.py ────────────────────────────────────────────────
const ADMIN    = { email: 'admin@mauekspor.example',  password: 'admin123'  };
const EXPORTER = { email: 'rizal@kopigayo.example',   password: 'rizal123'  };
const BUYER    = { email: 'aya@hikari.example',        password: 'buyer123'  };

// ─── All protected pages (route → screenshot folder name) ────────────────────
const ALL_PAGES: Array<{ route: string; name: string }> = [
  { route: '/dashboard',            name: '01-dashboard'          },
  { route: '/products',             name: '02-products'           },
  { route: '/export-analysis',      name: '03-export-analysis'    },
  { route: '/catalogs',             name: '04-catalogs'           },
  { route: '/costing',              name: '05-costing'            },
  { route: '/buyer-requests',       name: '06-buyer-requests'     },
  { route: '/buyers',               name: '07-buyers'             },
  { route: '/forwarders',           name: '08-forwarders'         },
  { route: '/markets',              name: '09-markets'            },
  { route: '/trade-projects',       name: '10-trade-projects'     },
  { route: '/business-profile',     name: '11-business-profile'   },
  { route: '/rfq',                  name: '12-rfq'                },
  { route: '/quotations',           name: '13-quotations'         },
  { route: '/orders',               name: '14-orders'             },
  { route: '/compliance',           name: '15-compliance'         },
  { route: '/documents',            name: '16-documents'          },
  { route: '/shipments',            name: '17-shipments'          },
  { route: '/payments',             name: '18-payments'           },
  { route: '/tasks',                name: '19-tasks'              },
  { route: '/notifications',        name: '20-notifications'      },
  { route: '/calendar',             name: '21-calendar'           },
  { route: '/messages',             name: '22-messages'           },
  { route: '/chat',                 name: '23-chat'               },
  { route: '/files',                name: '24-files'              },
  { route: '/reports',              name: '25-reports'            },
  { route: '/analytics',            name: '26-analytics'          },
  { route: '/audit',                name: '27-audit'              },
  { route: '/team',                 name: '28-team'               },
  { route: '/settings',             name: '29-settings'           },
  { route: '/billing',              name: '30-billing'            },
  { route: '/support',              name: '31-support'            },
  { route: '/api-keys',             name: '32-api-keys'           },
  { route: '/integrations',         name: '33-integrations'       },
  { route: '/automations',          name: '34-automations'        },
  { route: '/templates',            name: '35-templates'          },
  { route: '/knowledge',            name: '36-knowledge'          },
  { route: '/educational',          name: '37-educational'        },
  { route: '/marketing',            name: '38-marketing'          },
  { route: '/suppliers',            name: '39-suppliers'          },
  { route: '/countries',            name: '40-countries'          },
  { route: '/hs-codes',             name: '41-hs-codes'           },
  { route: '/users',                name: '42-users'              },
  { route: '/admin',                name: '43-admin'              },
];

// ─── Screenshot helper ───────────────────────────────────────────────────────
const SS_ROOT = path.join(process.cwd(), 'test-results', 'screenshots');

function ensureDir(dir: string) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

async function screenshotPage(page: Page, folderName: string) {
  const dir = path.join(SS_ROOT, folderName);
  ensureDir(dir);

  // 1. Full-page screenshot
  await page.screenshot({
    path: path.join(dir, '00-full-page.png'),
    fullPage: true,
  });

  // 2. Screenshot of every visible top-level section element
  const sectionSelectors = [
    'header',
    'nav',
    'main > section',
    'main > div > section',
    // card grids / stat cards
    '[class*="card"]',
    // data tables
    'table',
    // common SvelteKit layouts
    '[data-testid]',
    // headings with their siblings as context
    'h1', 'h2',
    // sidebar
    '[class*="sidebar"]',
    // toolbar / search bar area
    '[class*="toolbar"]',
    '[class*="filter"]',
    // footer
    'footer',
  ];

  const seen = new Set<string>();
  let idx = 1;

  for (const sel of sectionSelectors) {
    const elements = await page.locator(sel).all();
    for (const el of elements) {
      try {
        const visible = await el.isVisible();
        if (!visible) continue;

        // Bounding box dedup – skip duplicates that are fully inside an already-shot element
        const box = await el.boundingBox();
        if (!box) continue;
        const key = `${Math.round(box.x)},${Math.round(box.y)},${Math.round(box.width)},${Math.round(box.height)}`;
        if (seen.has(key)) continue;
        seen.add(key);

        // Skip tiny elements (< 100 px wide or tall)
        if (box.width < 100 || box.height < 30) continue;

        const filename = `${String(idx).padStart(2, '0')}-${sel.replace(/[^a-zA-Z0-9]/g, '_').replace(/_+/g, '_').slice(0, 30)}.png`;
        await el.screenshot({ path: path.join(dir, filename) });
        idx++;
      } catch {
        // element may have been removed after query – skip silently
      }
    }
  }
}

// ─── Login helper (persists cookies in context) ──────────────────────────────
async function loginAs(page: Page, creds: { email: string; password: string }) {
  await page.goto('/login');
  await page.waitForLoadState('networkidle');

  // Fill email – the id has a random suffix so we use type selector
  await page.locator('input[type="email"]').fill(creds.email);
  await page.locator('input[type="password"]').fill(creds.password);
  await page.click('button[type="submit"]');

  // Wait for navigation with longer timeout and less strict check
  try {
    await page.waitForNavigation({ timeout: 15_000 });
  } catch (e) {
    console.log('Navigation may take longer...');
  }
  
  // Give extra time for client-side routing
  await new Promise(r => setTimeout(r, 2000));
  
  const currentPath = new URL(page.url()).pathname;
  console.log(`After login, path: ${currentPath}`);
  
  if (!currentPath.includes('/login')) {
    console.log('Logged in successfully!');
  } else {
    // Try one more wait without forcing failure
    try {
      await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10_000 });
    } catch (e) {
      throw new Error('Login failed - unable to navigate away from /login');
    }
  }
  
  await page.waitForLoadState('networkidle');
}

// ─── Full page load helper ───────────────────────────────────────────────────
async function loadFully(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle');
  // Extra pause so lazy-loaded components, charts, AOS animations settle
  await page.waitForTimeout(1500);
}

// ═════════════════════════════════════════════════════════════════════════════
// TEST: Landing page (public)
// ═════════════════════════════════════════════════════════════════════════════
test('00 – Landing page (no auth) – screenshot all sections', async ({ page }) => {
  await page.goto('/');
  await loadFully(page);

  const dir = path.join(SS_ROOT, '00-landing');
  ensureDir(dir);

  // Full page
  await page.screenshot({ path: path.join(dir, '00-full-page.png'), fullPage: true });

  // Viewport (above the fold)
  await page.screenshot({ path: path.join(dir, '01-viewport.png') });

  // Scroll through the whole page and capture 6 vertical strips
  const totalHeight = await page.evaluate(() => document.body.scrollHeight);
  const viewH = page.viewportSize()!.height;
  const strips = Math.ceil(totalHeight / viewH);

  for (let i = 0; i < strips; i++) {
    await page.evaluate((y) => window.scrollTo(0, y), i * viewH);
    await page.waitForTimeout(400);
    await page.screenshot({ path: path.join(dir, `0${i + 2}-scroll-${i + 1}.png`) });
  }

  // Reset scroll
  await page.evaluate(() => window.scrollTo(0, 0));
});

// ═════════════════════════════════════════════════════════════════════════════
// TEST: Login page
// ═════════════════════════════════════════════════════════════════════════════
test('01 – Login page – screenshot', async ({ page }) => {
  await page.goto('/login');
  await loadFully(page);

  const dir = path.join(SS_ROOT, '00-login');
  ensureDir(dir);
  await page.screenshot({ path: path.join(dir, '00-full-page.png'), fullPage: true });
  await page.screenshot({ path: path.join(dir, '01-viewport.png') });
});

// ═════════════════════════════════════════════════════════════════════════════
// TEST SUITE – All protected pages (Admin role)
// ═════════════════════════════════════════════════════════════════════════════
test.describe('Protected pages – Admin role', () => {
  let ctx: BrowserContext;

  test.beforeAll(async ({ browser }) => {
    ctx = await browser.newContext();
    const pg = await ctx.newPage();
    await loginAs(pg, ADMIN);
    await pg.close();
  });

  test.afterAll(async () => { await ctx.close(); });

  for (const { route, name } of ALL_PAGES) {
    test(`${name} – ${route}`, async () => {
      const page = await ctx.newPage();
      try {
        await page.goto(route);
        await loadFully(page);

        // Verify the page actually loaded (not stuck on login)
        const currentPath = new URL(page.url()).pathname;
        expect(
          currentPath,
          `Expected to be on ${route} but got ${currentPath}`
        ).toContain(route.split('/')[1]);

        // Take screenshots
        await screenshotPage(page, name);

        // Additional: scroll through the whole page and capture vertical strips
        const pageDir = path.join(SS_ROOT, name);
        const totalHeight = await page.evaluate(() => document.body.scrollHeight);
        const viewH = page.viewportSize()!.height;
        const strips = Math.ceil(totalHeight / viewH);

        for (let i = 0; i < strips; i++) {
          await page.evaluate((y) => window.scrollTo(0, y), i * viewH);
          await page.waitForTimeout(300);
          await page.screenshot({ path: path.join(pageDir, `scroll-${String(i + 1).padStart(2, '0')}.png`) });
        }
      } finally {
        await page.close();
      }
    });
  }
});

// ═════════════════════════════════════════════════════════════════════════════
// TEST SUITE – Exporter role pages
// ═════════════════════════════════════════════════════════════════════════════
test.describe('Protected pages – Exporter role', () => {
  let ctx: BrowserContext;

  test.beforeAll(async ({ browser }) => {
    ctx = await browser.newContext();
    const pg = await ctx.newPage();
    await loginAs(pg, EXPORTER);
    await pg.close();
  });

  test.afterAll(async () => { await ctx.close(); });

  const EXPORTER_PAGES = [
    { route: '/dashboard',        name: 'exp-01-dashboard'     },
    { route: '/products',         name: 'exp-02-products'      },
    { route: '/export-analysis',  name: 'exp-03-export-analysis'},
    { route: '/catalogs',         name: 'exp-04-catalogs'      },
    { route: '/costing',          name: 'exp-05-costing'       },
    { route: '/forwarders',       name: 'exp-06-forwarders'    },
    { route: '/business-profile', name: 'exp-07-biz-profile'   },
    { route: '/compliance',       name: 'exp-08-compliance'    },
  ];

  for (const { route, name } of EXPORTER_PAGES) {
    test(`${name} – ${route}`, async () => {
      const page = await ctx.newPage();
      try {
        await page.goto(route);
        await loadFully(page);
        await screenshotPage(page, name);

        // Scroll captures
        const pageDir = path.join(SS_ROOT, name);
        const totalHeight = await page.evaluate(() => document.body.scrollHeight);
        const viewH = page.viewportSize()!.height;
        const strips = Math.ceil(totalHeight / viewH);
        for (let i = 0; i < strips; i++) {
          await page.evaluate((y) => window.scrollTo(0, y), i * viewH);
          await page.waitForTimeout(300);
          await page.screenshot({ path: path.join(pageDir, `scroll-${String(i + 1).padStart(2, '0')}.png`) });
        }
      } finally {
        await page.close();
      }
    });
  }
});

// ═════════════════════════════════════════════════════════════════════════════
// TEST SUITE – Buyer role pages
// ═════════════════════════════════════════════════════════════════════════════
test.describe('Protected pages – Buyer role', () => {
  let ctx: BrowserContext;

  test.beforeAll(async ({ browser }) => {
    ctx = await browser.newContext();
    const pg = await ctx.newPage();
    await loginAs(pg, BUYER);
    await pg.close();
  });

  test.afterAll(async () => { await ctx.close(); });

  const BUYER_PAGES = [
    { route: '/dashboard',         name: 'buy-01-dashboard'    },
    { route: '/buyer-requests',    name: 'buy-02-buyer-requests'},
    { route: '/quotations',        name: 'buy-03-quotations'   },
    { route: '/orders',            name: 'buy-04-orders'       },
    { route: '/buyers/my-profile', name: 'buy-05-my-profile'   },
  ];

  for (const { route, name } of BUYER_PAGES) {
    test(`${name} – ${route}`, async () => {
      const page = await ctx.newPage();
      try {
        await page.goto(route);
        await loadFully(page);
        await screenshotPage(page, name);

        const pageDir = path.join(SS_ROOT, name);
        const totalHeight = await page.evaluate(() => document.body.scrollHeight);
        const viewH = page.viewportSize()!.height;
        const strips = Math.ceil(totalHeight / viewH);
        for (let i = 0; i < strips; i++) {
          await page.evaluate((y) => window.scrollTo(0, y), i * viewH);
          await page.waitForTimeout(300);
          await page.screenshot({ path: path.join(pageDir, `scroll-${String(i + 1).padStart(2, '0')}.png`) });
        }
      } finally {
        await page.close();
      }
    });
  }
});
