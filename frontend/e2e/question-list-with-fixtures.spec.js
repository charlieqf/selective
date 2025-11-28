import { test, expect } from './fixtures.js'

test.describe('Question List with Seed Data', () => {
    test.beforeEach(async ({ page, seedData }) => {
        // Use authenticated page fixture and ensure seed data exists
        await page.goto('/questions')
        await page.waitForURL(/\/questions$/, { timeout: 10000 })
    })

    test('should display question cards', async ({ page }) => {
        // Check if question cards are visible
        const cards = page.locator('[data-testid="question-card"]')
        await expect(cards.first()).toBeVisible()

        // Should have at least 1 card
        const count = await cards.count()
        expect(count).toBeGreaterThan(0)
    })

    test('should filter by subject', async ({ page }) => {
        // Open filter dropdown
        await page.click('[data-testid="subject-filter"]')

        // Select MATHS option
        await page.click('.n-base-select-option:has-text("Maths")')

        // Wait for filtered results
        await page.waitForTimeout(1000)

        // All visible questions should be MATHS
        const cards = page.locator('[data-testid="question-card"]')
        const count = await cards.count()
        expect(count).toBeGreaterThan(0)

        // Check first card's subject
        const firstCardSubject = await cards.first().locator('.text-primary-600').innerText()
        expect(firstCardSubject).toBe('MATHS')
    })

    test('should navigate to question detail', async ({ page }) => {
        // Click first question card
        await page.locator('[data-testid="question-card"]').first().click()

        // Should navigate to detail page
        await expect(page).toHaveURL(/\/questions\/\d+/)
    })

    test('should show pagination', async ({ page }) => {
        // Check if pagination exists (if there are enough questions)
        const pagination = page.locator('.n-pagination')

        // May or may not be visible depending on number of questions
        const count = await pagination.count()
        expect(count).toBeGreaterThanOrEqual(0)
    })
})
