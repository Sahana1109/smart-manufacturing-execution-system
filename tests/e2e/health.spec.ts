import { test, expect } from '@playwright/test';

test('homepage displays SmartMES dashboard title', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('h1')).toContainText('Smart Manufacturing Execution System');
});

test('health diagnostics page loads system monitor', async ({ page }) => {
  await page.goto('/health');
  await expect(page.locator('h1')).toContainText('System Health & Diagnostic Monitor');
});
