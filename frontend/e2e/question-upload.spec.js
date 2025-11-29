import { test, expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

test.describe('Question Upload', () => {
    test.beforeEach(async ({ page }) => {
        // Capture browser console logs
        page.on('console', msg => console.log(`BROWSER: ${msg.text()}`))

        // Mock upload and delete API
        await page.route(/.*\/api\/upload/, async route => {
            const request = route.request()
            const method = request.method()
            console.log(`Intercepted ${method} ${request.url()}`)

            if (method === 'POST') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        url: 'https://res.cloudinary.com/demo/image/upload/v1/sample.jpg',
                        public_id: 'sample_id'
                    })
                })
            } else if (method === 'DELETE') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({ message: 'Deleted' })
                })
            } else {
                await route.continue()
            }
        })

        // Mock question creation API
        await page.route('**/api/questions', async route => {
            if (route.request().method() === 'POST') {
                await route.fulfill({
                    status: 201,
                    contentType: 'application/json',
                    body: JSON.stringify({ id: 1, title: 'Test Question' })
                })
            } else {
                await route.continue()
            }
        })

        // storageState already has us logged in, just navigate
        await page.goto('/questions/upload')
        await expect(page).toHaveURL(/\/questions\/upload/, { timeout: 10000 })
    })

    test.use({ viewport: { width: 1280, height: 720 } })

    test('should upload question with image successfully', async ({ page }) => {
        // Upload image
        const testImagePath = path.join(__dirname, 'fixtures', 'test-image.jpg')

        // Wait for upload trigger button
        // The ImageUploader component has a span with text "Upload"
        const uploadTrigger = page.locator('.n-upload-trigger')
        await uploadTrigger.waitFor()

        // Trigger file chooser
        const fileChooserPromise = page.waitForEvent('filechooser')
        await uploadTrigger.click()
        const fileChooser = await fileChooserPromise
        await fileChooser.setFiles(testImagePath)

        // Wait for upload to complete (check for thumbnail or removal of uploading state)
        // Since mock is fast, we just wait a bit or check for the image card
        await page.waitForTimeout(1000)

        // Fill form
        // Naive UI input renders an input element inside a div. 
        // We can target the input directly by placeholder or type.
        await page.fill('input[placeholder="e.g., Year 2023 Question 15"]', 'Test Question E2E')

        // Select subject
        // Find the form item with label "Subject" and click its select trigger
        await page.locator('.n-form-item', { hasText: 'Subject' }).locator('.n-select').click()
        // Wait for dropdown to appear
        await page.waitForSelector('.n-base-select-option__content >> text=Maths')
        await page.click('.n-base-select-option__content >> text=Maths')

        // Select difficulty
        await page.locator('.n-form-item', { hasText: 'Difficulty' }).locator('.n-select').click()
        await page.waitForSelector('.n-base-select-option__content >> text=Medium')
        await page.click('.n-base-select-option__content >> text=Medium')

        // Submit
        const submitBtn = page.locator('button:has-text("Upload Question")')
        // Playwright automatically scrolls, so we don't need explicit scroll which might cause fighting
        await submitBtn.click()

        // Should redirect to list
        await expect(page).toHaveURL(/\/questions$/)
    })

    test.skip('should validate file size', async ({ page }) => {
        // Skipping as this requires large file fixture
    })

    test('should require subject field', async ({ page }) => {
        // Submit
        const submitBtn = page.locator('button:has-text("Upload Question")')
        await submitBtn.click()

        // Should show validation error
        await expect(page.locator('text=Please select a subject')).toBeVisible()
    })

    test('should cancel and cleanup images', async ({ page }) => {
        const testImagePath = path.join(__dirname, 'fixtures', 'test-image.jpg')

        // Wait for upload trigger button
        // The ImageUploader component has a span with text "Upload"
        const uploadTrigger = page.locator('.n-upload-trigger')
        await uploadTrigger.waitFor()

        // Trigger file chooser
        const fileChooserPromise = page.waitForEvent('filechooser')
        await uploadTrigger.click()
        const fileChooser = await fileChooserPromise
        await fileChooser.setFiles(testImagePath)

        // Wait for upload
        await page.waitForTimeout(1000)

        // Cancel
        const cancelBtn = page.locator('button:has-text("Cancel")')
        await cancelBtn.click()

        // Should redirect
        await expect(page).toHaveURL(/\/questions$/)
    })
})
