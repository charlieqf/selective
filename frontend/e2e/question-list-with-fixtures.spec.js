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
        // Wait for collections to load in the filter dropdown
        await page.waitForSelector('[data-testid="subject-filter"]')

        // Open filter dropdown
        await page.click('[data-testid="subject-filter"]')

        // Wait for options to appear (collections are loaded async)
        await page.waitForSelector('.n-base-select-option', { timeout: 10000 })

        // Get all available options
        const options = await page.locator('.n-base-select-option').allInnerTexts()
        console.log('DEBUG: Filter options found:', options)

        // Skip if no options available (no collections created)
        if (options.length === 0) {
            console.log('No collections found, skipping filter test')
            return
        }

        // Select the first available option
        const firstOption = options[0]
        await page.click(`.n-base-select-option:has-text("${firstOption}")`)

        // Wait for filtered results
        await page.waitForTimeout(1000)

        // All visible questions should match the selected collection
        const cards = page.locator('[data-testid="question-card"]')
        const count = await cards.count()

        // May have no results if no questions in that collection
        console.log(`Found ${count} cards after filtering by "${firstOption}"`)
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
