import { chromium } from '@playwright/test'

async function globalSetup() {
    const browser = await chromium.launch()
    const context = await browser.newContext()
    const page = await context.newPage()

    try {
        // Navigate to login page
        await page.goto('http://localhost:5173/login')

        // Login
        await page.fill('input[placeholder="Username"]', 'testuser')
        await page.fill('input[placeholder="Password"]', 'password')
        await page.click('button:has-text("Sign in")')

        // Wait for login to complete and redirect to dashboard
        await page.waitForURL(/\/dashboard/, { timeout: 10000 })

        // CRITICAL: Wait a bit more to ensure localStorage is written
        await page.waitForTimeout(2000)

        // Verify localStorage was set
        const token = await page.evaluate(() => localStorage.getItem('access_token'))
        const user = await page.evaluate(() => localStorage.getItem('user'))

        if (!token || !user) {
            console.error('❌ localStorage not set after login!')
            console.log('token:', token)
            console.log('user:', user)
            throw new Error('Authentication failed - localStorage not set')
        }

        console.log('✓ localStorage verified:', { token: token.substring(0, 20) + '...', user: user.substring(0, 50) + '...' })

        // Save the authenticated state (includes localStorage via origins)
        await context.storageState({ path: 'e2e/.auth/testuser.json' })

        console.log('✓ Global setup complete: authenticated state saved')
    } catch (error) {
        console.error('❌ Global setup failed:', error.message)
        throw error
    } finally {
        await browser.close()
    }
}

export default globalSetup
