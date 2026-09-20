import { test, expect } from '@playwright/test';
import { Page } from '@playwright/test';

// Account credentials from seed.py
const ACCOUNTS = {
  admin: { email: 'admin@mauekspor.example', password: 'admin123', role: 'Admin' },
  exporter: { email: 'rizal@kopigayo.example', password: 'rizal123', role: 'Exporter' },
  buyer: { email: 'aya@hikari.example', password: 'buyer123', role: 'Buyer' }
};

const BASE_URL = 'http://localhost:5173';

// Helper function to wait for page to fully load
async function waitForFullLoad(page: Page) {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000); // Extra time for animations
}

// Helper function to take section screenshots
async function screenshotSections(page: Page, pageName: string, sections: string[]) {
  const screenshotDir = `test-results/screenshots/${pageName}`;
  
  for (let i = 0; i < sections.length; i++) {
    const selector = sections[i];
    try {
      // Try to find the element
      const element = page.locator(selector).first();
      if (await element.isVisible({ timeout: 2000 })) {
        await element.screenshot({ 
          path: `${screenshotDir}/section-${String(i + 1).padStart(2, '0')}.png` 
        });
        console.log(`✓ ${pageName} - Section ${i + 1} captured`);
      }
    } catch (e) {
      console.log(`⚠ ${pageName} - Section ${i + 1} not found or not visible`);
    }
  }
  
  // Always take full page screenshot
  await page.screenshot({ 
    path: `${screenshotDir}/full-page.png`,
    fullPage: true 
  });
  console.log(`✓ ${pageName} - Full page captured`);
}

// Login helper
async function login(page: Page, account: typeof ACCOUNTS.admin) {
  await page.goto(`${BASE_URL}/login`);
  await page.fill('input[name="email"]', account.email);
  await page.fill('input[name="password"]', account.password);
  await page.click('button[type="submit"]');
  await waitForFullLoad(page);
  await page.waitForURL('**/dashboard', { timeout: 10000 });
}

test.describe('Landing Page (Public)', () => {
  test('screenshot landing page sections', async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '01-landing', [
      'header', // Header/navigation
      'h1', // Hero section title
      '[class*="hero"]', // Hero section
      '[class*="features"]', // Features section
      '[class*="workflow"]', // Workflow section
      '[class*="testimonial"]', // Testimonials
      '[class*="cta"]', // Call to action
      'footer' // Footer
    ]);
  });
});

test.describe('Admin Pages', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ACCOUNTS.admin);
  });

  test('Dashboard', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '02-dashboard', [
      '[class*="sidebar"]', // Sidebar
      'h1, h2', // Page title
      '[class*="stat"]', // Stats cards
      '[class*="chart"]', // Charts
      '[class*="table"]' // Tables
    ]);
  });

  test('Products List', async ({ page }) => {
    await page.goto(`${BASE_URL}/products`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '03-products-list', [
      'h1, h2', // Page title
      '[class*="filter"]', // Filters
      '[class*="table"]', // Products table
      '[class*="pagination"]' // Pagination
    ]);
  });

  test('Business Profile', async ({ page }) => {
    await page.goto(`${BASE_URL}/business-profile`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '04-business-profile', [
      'h1, h2', // Page title
      '[class*="profile"]', // Profile info
      '[class*="certification"]', // Certifications
      'button' // Action buttons
    ]);
  });

  test('Export Analysis', async ({ page }) => {
    await page.goto(`${BASE_URL}/export-analysis`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '05-export-analysis', [
      'h1, h2', // Page title
      '[class*="analysis"]', // Analysis cards
      '[class*="compliance"]', // Compliance section
      '[class*="market"]' // Market analysis
    ]);
  });

  test('Catalogs', async ({ page }) => {
    await page.goto(`${BASE_URL}/catalogs`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '06-catalogs', [
      'h1, h2', // Page title
      '[class*="catalog"]', // Catalog cards
      '[class*="product"]' // Product info
    ]);
  });

  test('Costing', async ({ page }) => {
    await page.goto(`${BASE_URL}/costing`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '07-costing', [
      'h1, h2', // Page title
      '[class*="cost"]', // Cost breakdown
      '[class*="price"]', // Pricing info
      '[class*="container"]' // Container capacity
    ]);
  });

  test('Buyer Requests', async ({ page }) => {
    await page.goto(`${BASE_URL}/buyer-requests`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '08-buyer-requests', [
      'h1, h2', // Page title
      '[class*="request"]', // Request cards
      '[class*="match"]' // Match results
    ]);
  });

  test('Forwarders', async ({ page }) => {
    await page.goto(`${BASE_URL}/forwarders`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '09-forwarders', [
      'h1, h2', // Page title
      '[class*="forwarder"]', // Forwarder cards
      '[class*="rating"]', // Rating info
      '[class*="route"]' // Route info
    ]);
  });

  test('Quotations', async ({ page }) => {
    await page.goto(`${BASE_URL}/quotations`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '10-quotations', [
      'h1, h2', // Page title
      '[class*="quotation"]', // Quotation cards
      '[class*="status"]' // Status badges
    ]);
  });

  test('Orders', async ({ page }) => {
    await page.goto(`${BASE_URL}/orders`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '11-orders', [
      'h1, h2', // Page title
      '[class*="order"]', // Order cards
      '[class*="payment"]' // Payment info
    ]);
  });

  test('Compliance', async ({ page }) => {
    await page.goto(`${BASE_URL}/compliance`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '12-compliance', [
      'h1, h2', // Page title
      '[class*="requirement"]', // Requirements
      '[class*="evidence"]', // Evidence section
      '[class*="score"]' // Readiness score
    ]);
  });

  test('Documents', async ({ page }) => {
    await page.goto(`${BASE_URL}/documents`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '13-documents', [
      'h1, h2', // Page title
      '[class*="document"]', // Document cards
      '[class*="generate"]' // Generate buttons
    ]);
  });

  test('Shipments', async ({ page }) => {
    await page.goto(`${BASE_URL}/shipments`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '14-shipments', [
      'h1, h2', // Page title
      '[class*="shipment"]', // Shipment cards
      '[class*="milestone"]', // Milestones
      '[class*="tracking"]' // Tracking info
    ]);
  });

  test('Payments', async ({ page }) => {
    await page.goto(`${BASE_URL}/payments`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '15-payments', [
      'h1, h2', // Page title
      '[class*="payment"]', // Payment cards
      '[class*="invoice"]', // Invoice info
      '[class*="status"]' // Status badges
    ]);
  });

  test('Chat (AI)', async ({ page }) => {
    await page.goto(`${BASE_URL}/chat`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '16-chat', [
      'h1, h2', // Page title
      '[class*="session"]', // Chat sessions
      '[class*="message"]', // Messages
      '[class*="input"]' // Input area
    ]);
  });

  test('Messages', async ({ page }) => {
    await page.goto(`${BASE_URL}/messages`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '17-messages', [
      'h1, h2', // Page title
      '[class*="message"]', // Message cards
      '[class*="conversation"]' // Conversations
    ]);
  });

  test('Analytics', async ({ page }) => {
    await page.goto(`${BASE_URL}/analytics`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '18-analytics', [
      'h1, h2', // Page title
      '[class*="chart"]', // Charts
      '[class*="stat"]', // Statistics
      '[class*="overview"]' // Overview cards
    ]);
  });

  test('Reports', async ({ page }) => {
    await page.goto(`${BASE_URL}/reports`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '19-reports', [
      'h1, h2', // Page title
      '[class*="report"]', // Report cards
      '[class*="schedule"]' // Schedule info
    ]);
  });

  test('Knowledge Base', async ({ page }) => {
    await page.goto(`${BASE_URL}/knowledge`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '20-knowledge', [
      'h1, h2', // Page title
      '[class*="article"]', // Articles
      '[class*="category"]' // Categories
    ]);
  });

  test('Educational', async ({ page }) => {
    await page.goto(`${BASE_URL}/educational`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '21-educational', [
      'h1, h2', // Page title
      '[class*="module"]', // Modules
      '[class*="lesson"]' // Lessons
    ]);
  });

  test('Settings', async ({ page }) => {
    await page.goto(`${BASE_URL}/settings`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '22-settings', [
      'h1, h2', // Page title
      '[class*="setting"]', // Settings forms
      '[class*="company"]', // Company info
      '[class*="security"]' // Security settings
    ]);
  });

  test('Admin Panel', async ({ page }) => {
    await page.goto(`${BASE_URL}/admin`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '23-admin', [
      'h1, h2', // Page title
      '[class*="table"]', // Data tables
      '[class*="action"]', // Action buttons
      '[class*="modal"]' // Modals if any
    ]);
  });

  test('Notifications', async ({ page }) => {
    await page.goto(`${BASE_URL}/notifications`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '24-notifications', [
      'h1, h2', // Page title
      '[class*="notification"]', // Notification cards
      '[class*="unread"]' // Unread indicator
    ]);
  });

  test('Team', async ({ page }) => {
    await page.goto(`${BASE_URL}/team`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '25-team', [
      'h1, h2', // Page title
      '[class*="member"]', // Team members
      '[class*="invite"]' // Invite section
    ]);
  });

  test('API Keys', async ({ page }) => {
    await page.goto(`${BASE_URL}/api-keys`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '26-api-keys', [
      'h1, h2', // Page title
      '[class*="key"]', // API key cards
      '[class*="create"]' // Create button
    ]);
  });

  test('Audit Log', async ({ page }) => {
    await page.goto(`${BASE_URL}/audit`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '27-audit', [
      'h1, h2', // Page title
      '[class*="log"]', // Log entries
      '[class*="filter"]' // Filters
    ]);
  });

  test('Calendar', async ({ page }) => {
    await page.goto(`${BASE_URL}/calendar`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '28-calendar', [
      'h1, h2', // Page title
      '[class*="calendar"]', // Calendar view
      '[class*="event"]' // Events
    ]);
  });

  test('Tasks', async ({ page }) => {
    await page.goto(`${BASE_URL}/tasks`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '29-tasks', [
      'h1, h2', // Page title
      '[class*="task"]', // Task cards
      '[class*="status"]' // Status indicators
    ]);
  });

  test('Templates', async ({ page }) => {
    await page.goto(`${BASE_URL}/templates`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '30-templates', [
      'h1, h2', // Page title
      '[class*="template"]', // Template cards
      '[class*="use"]' // Use buttons
    ]);
  });

  test('Automations', async ({ page }) => {
    await page.goto(`${BASE_URL}/automations`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '31-automations', [
      'h1, h2', // Page title
      '[class*="automation"]', // Automation cards
      '[class*="trigger"]' // Trigger info
    ]);
  });

  test('Integrations', async ({ page }) => {
    await page.goto(`${BASE_URL}/integrations`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '32-integrations', [
      'h1, h2', // Page title
      '[class*="integration"]', // Integration cards
      '[class*="connect"]' // Connect buttons
    ]);
  });

  test('Billing', async ({ page }) => {
    await page.goto(`${BASE_URL}/billing`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '33-billing', [
      'h1, h2', // Page title
      '[class*="plan"]', // Plan cards
      '[class*="invoice"]', // Invoice history
      '[class*="upgrade"]' // Upgrade button
    ]);
  });

  test('Support', async ({ page }) => {
    await page.goto(`${BASE_URL}/support`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '34-support', [
      'h1, h2', // Page title
      '[class*="ticket"]', // Support tickets
      '[class*="create"]' // Create button
    ]);
  });

  test('Countries', async ({ page }) => {
    await page.goto(`${BASE_URL}/countries`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '35-countries', [
      'h1, h2', // Page title
      '[class*="country"]', // Country cards
      '[class*="regulation"]' // Regulation info
    ]);
  });

  test('HS Codes', async ({ page }) => {
    await page.goto(`${BASE_URL}/hs-codes`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '36-hs-codes', [
      'h1, h2', // Page title
      '[class*="hs"]', // HS code cards
      '[class*="search"]' // Search bar
    ]);
  });

  test('Users (Admin)', async ({ page }) => {
    await page.goto(`${BASE_URL}/users`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '37-users', [
      'h1, h2', // Page title
      '[class*="user"]', // User cards
      '[class*="role"]', // Role badges
      '[class*="table"]' // Users table
    ]);
  });
});

test.describe('Exporter Pages (Exporter Role)', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ACCOUNTS.exporter);
  });

  test('Exporter Dashboard', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '38-exporter-dashboard', [
      'h1, h2',
      '[class*="stat"]',
      '[class*="chart"]'
    ]);
  });
});

test.describe('Buyer Pages (Buyer Role)', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ACCOUNTS.buyer);
  });

  test('Buyer Dashboard', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '39-buyer-dashboard', [
      'h1, h2',
      '[class*="stat"]',
      '[class*="request"]'
    ]);
  });

  test('My Buyer Profile', async ({ page }) => {
    await page.goto(`${BASE_URL}/buyers/my-profile`);
    await waitForFullLoad(page);
    
    await screenshotSections(page, '40-buyer-profile', [
      'h1, h2',
      '[class*="profile"]',
      '[class*="preference"]'
    ]);
  });
});
