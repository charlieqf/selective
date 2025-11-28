import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
    test.beforeEach(async ({ page }) => {
        // storageState already has us logged in, just navigate
        await page.goto('/dashboard')
        await page.waitForSelector('text=Total Questions', { timeout: 10000 })
    })

    test('should display welcome message', async ({ page }) => {
        await expect(page.locator('h1:has-text("Welcome back")')).toBeVisible()
    })

    test('should display statistics cards', async ({ page }) => {
        // Check for stat cards (they exist in dashboard)
        const cards = page.locator('.n-card')
        await expect(cards.first()).toBeVisible()
    })

    test('should have upload button', async ({ page }) => {
        const uploadBtn = page.locator('button:has-text("Upload New Question")')
        await expect(uploadBtn).toBeVisible()

        // Click and navigate
        await uploadBtn.click()
        await expect(page).toHaveURL(/\/questions\/upload/, { timeout: 5000 })
    })

    test('should have view all button', async ({ page }) => {
        const viewAllBtn = page.locator('button:has-text("View All Questions")')
        await expect(viewAllBtn).toBeVisible()
    })
})
