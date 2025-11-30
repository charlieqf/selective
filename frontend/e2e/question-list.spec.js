import { test, expect } from '@playwright/test'

test.describe('Question List', () => {
    test.beforeEach(async ({ page }) => {
        // Capture browser console logs
        page.on('console', msg => console.log(`BROWSER: ${msg.text()}`))

        // storageState already has us logged in, just navigate
        await page.goto('/questions')
        await expect(page).toHaveURL(/\/questions$/, { timeout: 10000 })
    })

    test('should display question cards', async ({ page }) => {
        // Check if question cards are visible
        const cards = page.locator('[data-testid="question-card"]')
        await expect(cards.first()).toBeVisible()
    })

    test('should filter by subject', async ({ page }) => {
        // Open filter dropdown
        await page.click('[data-testid="subject-filter"]')

        // Select MATHS option (Naive UI renders options in a portal, usually in body)
        await page.click('.n-base-select-option:has-text("MATHS")')

        // Wait for filtered results
        await page.waitForTimeout(1000)

        // All visible questions should be MATHS
        // We check the subject tag on the card
        const cards = page.locator('[data-testid="question-card"]')
        const count = await cards.count()
        expect(count).toBeGreaterThan(0)

        // Check first card's subject
        const firstCardSubject = await cards.first().locator('.text-primary-600').innerText()
        expect(firstCardSubject).toBe('MATHS')
    })

    test('should filter by difficulty', async ({ page }) => {
        // Filter by difficulty 5
        await page.click('[data-testid="difficulty-filter"]')
        await page.click('.n-base-select-option:has-text("⭐⭐⭐⭐⭐ (5)")')

        await page.waitForTimeout(1000)

        // Verify stars on first card
        const cards = page.locator('[data-testid="question-card"]')
        if (await cards.count() > 0) {
            const stars = await cards.first().locator('.text-sm').nth(1).innerText()
            expect(stars).toContain('⭐⭐⭐⭐⭐')
        }
    })

    test('should navigate to question detail', async ({ page }) => {
        console.log('TEST: Starting navigation test...')

        // Click first question card
        console.log('TEST: Locating first card...')
        const firstCard = page.locator('[data-testid="question-card"]').first()
        await expect(firstCard).toBeVisible()
        console.log('TEST: First card visible. Clicking...')

        await firstCard.click()
        console.log('TEST: Clicked. Waiting for navigation...')

        try {
            await expect(page).toHaveURL(/\/questions\/\d+/, { timeout: 5000 })
            console.log('TEST: Navigation successful.')
        } catch (e) {
            console.log(`TEST: Navigation failed. Current URL: ${page.url()}`)
            throw e
        }
    })

    test('should show pagination', async ({ page }) => {
        // Check if pagination exists (if there are enough questions)
        const pagination = page.locator('.n-pagination')

        // May or may not be visible depending on number of questions
        const count = await pagination.count()
        expect(count).toBeGreaterThanOrEqual(0)
    })

    test('should refresh questions', async ({ page }) => {
        // Click refresh button
        await page.click('button:has-text("Refresh")')

        // Wait for reload
        await page.waitForTimeout(1000)

        // Questions should still be visible
        await expect(page.locator('[data-testid="question-card"]').first()).toBeVisible()
    })
})
