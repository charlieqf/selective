import { test, expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

test.describe('Tags Feature', () => {
    test.beforeEach(async ({ page }) => {
        // Capture browser console logs
        page.on('console', msg => console.log(`BROWSER: ${msg.text()}`))

        // Mock upload API
        await page.route('**/api/upload', async route => {
            if (route.request().method() === 'POST') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        url: 'https://res.cloudinary.com/demo/image/upload/v1/sample.jpg',
                        public_id: 'sample_id'
                    })
                })
            } else {
                await route.continue()
            }
        })

        // Mock collections API
        await page.route('**/api/collections', async route => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify([
                        { id: 1, name: 'MATHS', icon: 'calculator', color: '#10b981', is_deleted: false }
                    ])
                })
            } else {
                await route.continue()
            }
        })

        // Mock tags API (autocomplete)
        await page.route('**/api/tags', async route => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify([
                        { id: 1, name: 'algebra' },
                        { id: 2, name: 'geometry' }
                    ])
                })
            } else {
                await route.continue()
            }
        })

        // Mock items API
        // Use regex to match /api/items with optional query params, but avoid matching .js files
        await page.route(/\/api\/items($|\?)/, async route => {
            const request = route.request()
            const url = new URL(request.url())

            if (request.method() === 'POST') {
                // Verify payload
                const data = request.postDataJSON()
                console.log('POST /api/items payload:', data)

                await route.fulfill({
                    status: 201,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        id: 1,
                        ...data,
                        created_at: new Date().toISOString()
                    })
                })
            } else if (request.method() === 'GET') {
                // Check if filtering by tag
                const tagParams = url.searchParams.getAll('tag')
                let items = []

                if (tagParams.length > 0) {
                    // Return filtered items
                    if (tagParams.includes('algebra')) {
                        items = [{
                            id: 1,
                            title: 'Algebra Question',
                            collection_id: 1,
                            difficulty: 3,
                            status: 'UNANSWERED',
                            tags: [{ id: 1, name: 'algebra' }, { id: 3, name: 'hard' }],
                            images: [{ url: 'sample.jpg' }],
                            created_at: new Date().toISOString()
                        }]
                    }
                } else {
                    // Return all items
                    items = [
                        {
                            id: 1,
                            title: 'Algebra Question',
                            collection_id: 1,
                            difficulty: 3,
                            status: 'UNANSWERED',
                            tags: [{ id: 1, name: 'algebra' }, { id: 3, name: 'hard' }],
                            images: [{ url: 'sample.jpg' }],
                            created_at: new Date().toISOString()
                        },
                        {
                            id: 2,
                            title: 'Geometry Question',
                            collection_id: 1,
                            difficulty: 2,
                            status: 'ANSWERED',
                            tags: [{ id: 2, name: 'geometry' }],
                            images: [{ url: 'sample.jpg' }],
                            created_at: new Date().toISOString()
                        }
                    ]
                }

                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        items,
                        total: items.length,
                        pages: 1,
                        current_page: 1
                    })
                })
            } else {
                await route.continue()
            }
        })
    })

    test('should create item with tags', async ({ page }) => {
        await page.goto('/questions/upload')

        // Upload image
        const testImagePath = path.join(__dirname, 'fixtures', 'test-image.jpg')
        const uploadTrigger = page.locator('.n-upload-trigger')
        await uploadTrigger.waitFor()

        const fileChooserPromise = page.waitForEvent('filechooser')
        await uploadTrigger.click()
        const fileChooser = await fileChooserPromise
        await fileChooser.setFiles(testImagePath)
        await page.waitForSelector('.n-upload-file-info')

        // Fill basic info
        await page.fill('input[placeholder="e.g., Year 2023 Question 15"]', 'Tagged Question')

        // Select subject
        await page.click('.n-form-item:has-text("Subject") .n-select')
        await page.locator('.n-base-select-option', { hasText: 'MATHS' }).click()

        // Add tags
        console.log('TEST: Clicking tag input...')
        const tagInput = page.locator('.n-form-item:has-text("Tags") .n-select')
        await tagInput.click()

        // Select existing tag 'algebra'
        console.log('TEST: Selecting algebra...')
        await page.locator('.n-base-select-option', { hasText: 'algebra' }).click()

        // Create new tag 'hard'
        console.log('TEST: Creating new tag hard...')
        await page.keyboard.type('hard')
        await page.waitForTimeout(200)
        await page.keyboard.press('Enter')

        // Wait a bit for UI to update
        await page.waitForTimeout(500)

        // Submit
        console.log('TEST: Clicking submit...')
        await page.click('button:has-text("Upload Question")')

        try {
            await page.waitForURL(/\/questions$/, { timeout: 5000 })
        } catch (e) {
            console.log('TEST: Navigation timeout. Checking for errors...')
            const errors = await page.locator('.n-form-item-feedback__line').allInnerTexts().catch(() => [])
            console.log('TEST: Validation errors:', errors)
            const toasts = await page.locator('.n-message__content').allInnerTexts().catch(() => [])
            console.log('TEST: Toasts:', toasts)
            throw e
        }
    })

    test('should display and filter tags in list', async ({ page }) => {
        await page.goto('/questions')

        // Verify tags are displayed on card
        const card = page.locator('[data-testid="question-card"]').first()
        await expect(card).toBeVisible()
        // Note: QuestionCard renders tags with # prefix
        await expect(card.locator('[data-testid="card-tag"]:has-text("#algebra")')).toBeVisible()
        await expect(card.locator('[data-testid="card-tag"]:has-text("#hard")')).toBeVisible()

        // Click tag to filter
        await card.locator('[data-testid="card-tag"]:has-text("#algebra")').click()

        // Verify URL and active filter
        await expect(page).toHaveURL(/tag=algebra/)

        // Wait a bit for active tags to render
        await page.waitForTimeout(500)

        await expect(page.locator('text=Active Tags:')).toBeVisible()
        // Use more specific selector: bg-primary-100 text-primary-800 rounded-full
        await expect(page.locator('.bg-primary-100.rounded-full:has-text("#algebra")')).toBeVisible()

        // Verify list is filtered (mock returns only 1 item when filtered)
        const cards = page.locator('[data-testid="question-card"]')
        await expect(cards).toHaveCount(1)
        await expect(cards.first().locator('[data-testid="card-title"]')).toHaveText('Algebra Question')

        // Clear filter
        await page.click('button:has-text("Clear All")')
        await expect(page).not.toHaveURL(/tag=algebra/)
        await expect(cards).toHaveCount(2)
    })
})
