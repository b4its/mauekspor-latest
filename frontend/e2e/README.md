# Playwright E2E Testing - MauEkspor

## Overview
This directory contains end-to-end tests for the MauEkspor frontend using Playwright. The tests navigate through all pages, take screenshots of each section, and verify that pages load completely.

## Test Coverage
The test suite covers **40 test scenarios** across all user roles:

### Public Pages (No Auth)
- Landing page with all sections (hero, features, workflow, testimonials, CTA, footer)

### Admin Role (admin@mauekspor.example / admin123)
- Dashboard
- Products management
- Business Profile
- Export Analysis
- Catalogs
- Costing calculator
- Buyer Requests
- Forwarders
- Quotations
- Orders
- Compliance requirements
- Documents
- Shipments
- Payments
- Chat (AI)
- Messages
- Analytics
- Reports
- Knowledge Base
- Educational modules
- Settings
- Admin Panel
- Notifications
- Team management
- API Keys
- Audit Log
- Calendar
- Tasks
- Templates
- Automations
- Integrations
- Billing
- Support
- Countries
- HS Codes
- Users management

### Exporter Role (rizal@kopigayo.example / rizal123)
- Exporter Dashboard

### Buyer Role (aya@hikari.example / buyer123)
- Buyer Dashboard
- My Buyer Profile

## Screenshots
Each test captures:
1. **Section screenshots**: Individual sections of each page (headers, stats, tables, forms, etc.)
2. **Full page screenshot**: Complete page capture

Screenshots are saved to: `test-results/screenshots/{test-name}/`

## Prerequisites
Before running tests, ensure both backend and frontend servers are running:

### Start Backend
```bash
cd ../backend
MAUEKSPOR_DATABASE_URL=sqlite:///./mauekspor.db .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Start Frontend
```bash
pnpm dev
```

## Running Tests

### Run all tests
```bash
pnpm exec playwright test
```

### Run specific test file
```bash
pnpm exec playwright test e2e/screenshot-all-pages.spec.ts
```

### Run with UI mode (interactive)
```bash
pnpm exec playwright test --ui
```

### Run specific test by name
```bash
pnpm exec playwright test -g "Dashboard"
```

### Run with headed browser (see what's happening)
```bash
pnpm exec playwright test --headed
```

### Run with slow motion (easier to follow)
```bash
pnpm exec playwright test --headed --slow-mo=1000
```

## Viewing Test Results

### HTML Report
```bash
pnpm exec playwright show-report
```

### Screenshots
Navigate to `test-results/screenshots/` to view all captured screenshots organized by page.

## Test Structure

Each test follows this pattern:
1. **Login** with appropriate credentials (Admin/Exporter/Buyer)
2. **Navigate** to the target page
3. **Wait for full load** (networkidle + 1 second delay)
4. **Capture sections**: Individual elements like headers, stats, tables
5. **Capture full page**: Complete page screenshot

## Troubleshooting

### Tests fail with timeout
- Ensure backend is running on port 8000
- Ensure frontend is running on port 5173
- Check if seed data exists (run seed.py if needed)

### Screenshots are blank or incomplete
- Increase wait time in `waitForFullLoad()` function
- Check if page requires specific data to render

### Login fails
- Verify seed accounts exist in database
- Check if backend authentication is working

## Configuration
Edit `playwright.config.ts` to customize:
- Browser types (Chromium, Firefox, WebKit)
- Test timeout
- Screenshot behavior
- Retry attempts

## Account Credentials
From `backend/app/seed.py`:
- **Admin**: admin@mauekspor.example / admin123
- **Exporter**: rizal@kopigayo.example / rizal123
- **Buyer**: aya@hikari.example / buyer123
