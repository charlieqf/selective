import { test, expect } from '@playwright/test'

test.describe('Quickbr Tests', () => {
    // Reset storage state for this file to ensure we are not logged in
    test.use({ storageState: { cookies: [], origins: [] } })

    test('should login successfully', async ({ page }) => {
        await page.goto('/login')
        await page.fill('input[placeholder="Username"]', 'testuser')
        await page.fill('input[placeholder="Password"]', 'password')
        await page.click('button:has-text("Sign in")')

        await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 })
    })

    test('should redirect unauthorized access', async ({ page }) => {
        await page.goto('/dashboard')
        await expect(page).toHaveURL(/\/login/, { timeout: 5000 })
    })
})
