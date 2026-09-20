// This script should be run from the frontend directory

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SCREENSHOT_DIR = '/home/vxm/programming/mauekspor/screenshots';

// Login credentials from seed.py
const ADMIN_CREDENTIALS = {
  email: 'admin@mauekspor.example',
  password: 'admin123'
};

// All pages to screenshot (protected routes)
const PAGES = [
  '/dashboard',
  '/products',
  '/export-analysis',
  '/catalogs',
  '/costing',
  '/buyer-requests',
  '/buyers',
  '/forwarders',
  '/markets',
  '/trade-projects',
  '/business-profile',
  '/rfq',
  '/quotations',
  '/orders',
  '/compliance',
  '/documents',
  '/shipments',
  '/payments',
  '/tasks',
  '/notifications',
  '/calendar',
  '/messages',
  '/chat',
  '/files',
  '/reports',
  '/analytics',
  '/audit',
  '/team',
  '/settings',
  '/billing',
  '/support',
  '/api-keys',
  '/integrations',
  '/automations',
  '/templates',
  '/knowledge',
  '/educational',
  '/marketing',
  '/suppliers',
  '/countries',
  '/hs-codes',
  '/users',
  '/admin'
];

// Helper: ensure directory exists
function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

// Helper: login to the app
async function login(page) {
  console.log('Logging in...');
  await page.goto('/login', { waitUntil: 'networkidle' });
  
  // Fill credentials - using type selectors since IDs may be dynamic
  await page.fill('input[type="email"]', ADMIN_CREDENTIALS.email);
  await page.fill('input[type="password"]', ADMIN_CREDENTIALS.password);
  await page.click('button[type="submit"]');
  
  // Wait for navigation away from /login
  await page.waitForNavigation({ waitUntil: 'networkidle', timeout: 20000 });
  await page.waitForLoadState('networkidle');
  console.log('Logged in successfully!');
}

// Helper: fully load a page with animations and lazy content
async function loadPageFully(page, url) {
  await page.goto(url, { waitUntil: 'networkidle' });
  // Give time for lazy loading, AOS animations, charts to render
  await new Promise(r => setTimeout(r, 2000));
  return page.url();
}

// Helper: capture full-page screenshot
async function captureFullPage(page, outputPath) {
  await page.screenshot({ path: outputPath, fullPage: true });
}

// Helper: capture individual sections on the page
async function captureSections(page, dirPath) {
  const sectionSelectors = [
    'header',
    'main > section',
    'main > div > section',
    '[class*="card"]',
    'table',
    '[data-testid]',
    'h1',
    'h2',
    '[class*="sidebar"]',
    '[class*="toolbar"]',
    '[class*="filter"]',
    'footer'
  ];

  const seen = new Set();
  let idx = 1;

  for (const selector of sectionSelectors) {
    const elements = await page.locator(selector).all();
    
    for (const element of elements) {
      try {
        const visible = await element.isVisible();
        if (!visible) continue;

        const box = await element.boundingBox();
        if (!box) continue;

        // Skip tiny elements
        if (box.width < 100 || box.height < 50) continue;

        // Deduplicate by position/size
        const key = `${Math.round(box.x)},${Math.round(box.y)},${Math.round(box.width)},${Math.round(box.height)}`;
        if (seen.has(key)) continue;
        seen.add(key);

        const filename = `${String(idx).padStart(3, '0')}-${selector.replace(/[^a-zA-Z0-9]/g, '_').replace(/_+/g, '_').slice(0, 30)}.png`;
        await element.screenshot({ path: path.join(dirPath, filename) });
        idx++;
      } catch (err) {
        // Element may have changed state between query and screenshot
      }
    }
  }
  
  console.log(`  Captured ${idx - 1} sections`);
}

// Main function
async function main() {
  console.log('Starting screenshot session...\n');
  
  // Launch browser
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  // Create screenshot directory structure
  ensureDir(SCREENSHOT_DIR);

  try {
    // Step 1: Login first
    await login(page);

    // Step 2: Loop through all pages
    console.log('\nProcessing pages...\n');
    
    for (let i = 0; i < PAGES.length; i++) {
      const pagePath = PAGES[i];
      const pageName = `0${i + 1}${pagePath.split('/')[1] || 'root'}`;
      const dirPath = path.join(SCREENSHOT_DIR, pageName);
      
      console.log(`[${i + 1}/${PAGES.length}] Processing: ${pagePath}`);
      
      try {
        // Ensure directory
        ensureDir(dirPath);

        // Load page fully
        await loadPageFully(page, pagePath);

        // Check we're on the right page
        const currentUrl = page.url();
        console.log(`   Current URL: ${currentUrl}`);

        // Full-page screenshot
        const fullPath = path.join(dirPath, '001-full-page.png');
        await captureFullPage(page, fullPath);
        
        // Scroll-through screenshots (vertical strips)
        const totalHeight = await page.evaluate(() => document.body.scrollHeight);
        const viewHeight = 900;
        const numStrips = Math.ceil(totalHeight / viewHeight);

        for (let strip = 0; strip < numStrips; strip++) {
          const yPos = strip * viewHeight;
          await page.evaluate((y) => window.scrollTo(0, y), yPos);
          await new Promise(r => setTimeout(r, 300));
          
          const stripPath = path.join(dirPath, `002-scroll-${String(strip + 1).padStart(3, '0')}.png`);
          await page.screenshot({ path: stripPath, clip: { x: 0, y: yPos, width: 1440, height: Math.min(viewHeight, totalHeight - yPos) } });
        }

        // Section screenshots
        await captureSections(page, dirPath);

        console.log(`   ✓ Saved to ${dirPath}\n`);

      } catch (err) {
        console.error(`   ✗ Error processing ${pagePath}:`, err.message);
        
        // Try to capture error screenshot anyway
        try {
          const dirPath = path.join(SCREENSHOT_DIR, pageName);
          ensureDir(dirPath);
          await captureFullPage(page, path.join(dirPath, 'error.png'));
        } catch {}
        
        console.log('');
      }
    }

    console.log('\n✅ Screenshot session completed!\n');

  } finally {
    await browser.close();
  }
}

// Run
main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
