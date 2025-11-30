import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
    // Reset storage state for this file to ensure we are not logged in
    test.use({ storageState: { cookies: [], origins: [] } })

    test.beforeEach(async ({ page }) => {
        // Capture browser console logs
        page.on('console', msg => console.log(`BROWSER: ${msg.text()}`))
        await page.goto('/')
    })

    test('should register as student and auto-login', async ({ page }) => {
        const randomId = Math.floor(Math.random() * 10000)
        const username = `student${randomId}`

        // Navigate to register
        await page.click('text=Create account')

        // Fill registration form
        await page.fill('input[placeholder="Username"]', username)
        await page.fill('input[placeholder="Email"]', `${username}@example.com`)
        await page.fill('input[placeholder="Password"]', 'password123')
        await page.fill('input[placeholder="Confirm Password"]', 'password123')

        // Select student role
        await page.click('text=Student')

        // Submit
        await page.click('button:has-text("Register")')

        // Should redirect to dashboard
        await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 })
    })

    test('should register as parent', async ({ page }) => {
        const randomId = Math.floor(Math.random() * 10000)
        const username = `parent${randomId}`

        await page.click('text=Create account')
        await page.fill('input[placeholder="Username"]', username)
        await page.fill('input[placeholder="Email"]', `${username}@example.com`)
        await page.fill('input[placeholder="Password"]', 'password123')
        await page.fill('input[placeholder="Confirm Password"]', 'password123')

        // Select parent role
        await page.click('text=Parent')

        await page.click('button:has-text("Register")')

        // Verify logged in
        await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 })
    })

    test('should login with correct credentials', async ({ page }) => {
        // Use existing test user (created in backend fixtures)
        await page.goto('/login')

        await page.fill('input[placeholder="Username"]', 'testuser')
        await page.fill('input[placeholder="Password"]', 'password')

        // Correct button text is "Sign in"
        await page.click('button:has-text("Sign in")')

        await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 })
    })

    test('should show error for wrong credentials', async ({ page }) => {
        await page.goto('/login')

        await page.fill('input[placeholder="Username"]', 'wronguser')
        await page.fill('input[placeholder="Password"]', 'wrongpass')

        await page.click('button:has-text("Sign in")')

        // Should show error message (toast notification)
        await page.waitForTimeout(1000)
        // Error might appear in different ways, check for common patterns
        const hasError = await page.locator('text=/Invalid|Error|failed/i').count()
        expect(hasError).toBeGreaterThan(0)
    })

    test('should redirect unauthenticated user to login', async ({ page }) => {
        await page.goto('/dashboard')

        // Should redirect to login
        await expect(page).toHaveURL(/\/login/, { timeout: 5000 })
    })

    test('should logout successfully', async ({ page }) => {
        // Login first
        await page.goto('/login')
        await page.fill('input[placeholder="Username"]', 'testuser')
        await page.fill('input[placeholder="Password"]', 'password')
        await page.click('button:has-text("Sign in")')

        await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 })

        // Logout - find logout button
        await page.click('text=Logout')

        // Should redirect to login
        await expect(page).toHaveURL(/\/login/, { timeout: 5000 })

        // Try accessing dashboard again
        await page.goto('/dashboard')
        await expect(page).toHaveURL(/\/login/, { timeout: 5000 })
    })
})
