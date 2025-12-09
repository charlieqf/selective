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

    test('should display Collections section with counts', async ({ page }) => {
        // Check for Collections heading
        const collectionsHeading = page.locator('h2:has-text("Collections")')
        await expect(collectionsHeading).toBeVisible()

        // Check that collection cards exist (if any)
        const collectionCards = page.locator('.n-card:has-text("Total:")')
        const count = await collectionCards.count()

        if (count > 0) {
            // Verify first collection card has the expected structure
            const firstCard = collectionCards.first()
            await expect(firstCard.locator('text=Total:')).toBeVisible()
            await expect(firstCard.locator('text=Need Review:')).toBeVisible()
        }
    })

    test('should navigate to review list when clicking Review button', async ({ page }) => {
        // Find a Review button (only visible if need_review_count > 0)
        const reviewBtn = page.locator('button:has-text("Review (")').first()
        const hasReviewBtn = await reviewBtn.count() > 0

        if (hasReviewBtn) {
            await reviewBtn.click()
            // Should navigate to questions list with needs_review filter
            await expect(page).toHaveURL(/\/questions\?.*needs_review=true/, { timeout: 5000 })
        }
    })
})
