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
        await page.route('**/api/upload', async route => {
            const request = route.request()
            console.log(`Intercepted UPLOAD ${request.method()} ${request.url()}`)

            if (request.method() === 'POST') {
                const response = {
                    url: 'https://res.cloudinary.com/demo/image/upload/v1/sample.jpg',
                    public_id: 'sample_id'
                }
                console.log('Mock returning UPLOAD:', JSON.stringify(response))
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify(response)
                })
            } else if (request.method() === 'DELETE') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({ message: 'Deleted' })
                })
            } else {
                await route.continue()
            }
        })

        // Mock collections API
        await page.route('**/api/collections', async route => {
            console.log(`Intercepted COLLECTIONS ${route.request().method()} ${route.request().url()}`)
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify([
                        { id: 1, name: 'READING', icon: 'book', color: '#f97316', is_deleted: false },
                        { id: 2, name: 'WRITING', icon: 'pencil', color: '#a855f7', is_deleted: false },
                        { id: 3, name: 'MATHS', icon: 'calculator', color: '#10b981', is_deleted: false },
                        { id: 4, name: 'THINKING_SKILLS', icon: 'brain', color: '#6366f1', is_deleted: false }
                    ])
                })
                return
            }
            await route.continue()
        })

        // Mock question creation API
        await page.route('**/api/items*', async route => {
            const request = route.request()
            console.log(`Intercepted ITEMS ${request.method()} ${request.url()}`)

            if (request.method() === 'POST') {
                const response = {
                    id: 1,
                    title: 'Test Question',
                    collection_id: 1,
                    difficulty: 3,
                    images: [{ url: 'https://res.cloudinary.com/demo/image/upload/v1/sample.jpg', public_id: 'sample_id' }]
                }
                console.log('Mock returning ITEMS:', JSON.stringify(response))
                await route.fulfill({
                    status: 201,
                    contentType: 'application/json',
                    body: JSON.stringify(response)
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
        const uploadTrigger = page.locator('.n-upload-trigger')
        await uploadTrigger.waitFor()

        // Trigger file chooser
        const fileChooserPromise = page.waitForEvent('filechooser')
        await uploadTrigger.click()
        const fileChooser = await fileChooserPromise
        await fileChooser.setFiles(testImagePath)

        // Wait for upload to complete - verify image card appears
        await page.waitForSelector('.n-upload-file-info', { timeout: 5000 })
        console.log('TEST: Image upload confirmed')

        // Fill form
        await page.fill('input[placeholder="e.g., Year 2023 Question 15"]', 'Test Question E2E')

        // Select subject (backed by collection)
        const subjectSelect = page.locator('.n-form-item', { hasText: 'Subject' }).locator('.n-select')
        await subjectSelect.click()
        await page.waitForSelector('.n-base-select-option__content')
        await page.click('.n-base-select-option__content:has-text("READING")')
        await expect(subjectSelect).toHaveText(/READING/)
        // Ensure value is set in the model
        await page.waitForTimeout(500)
        console.log('TEST: Subject selected')

        // Select difficulty - use partial text match since label includes stars
        const difficultySelect = page.locator('.n-form-item', { hasText: 'Difficulty' }).locator('.n-select')
        await difficultySelect.click()
        await page.waitForTimeout(300)
        await page.click('.n-base-select-option__content:has-text("Medium")')
        await expect(difficultySelect).toHaveText(/Medium/)
        await page.waitForTimeout(500)
        console.log('TEST: Difficulty selected')

        //Debug: Check form values
        const titleValue = await page.inputValue('input[placeholder="e.g., Year 2023 Question 15"]')
        console.log('TEST: Title value:', titleValue)

        // Submit
        const submitBtn = page.locator('button:has-text("Upload Question")')
        console.log('TEST: Clicking submit button...')
        await submitBtn.click()

        // Wait for navigation to complete
        console.log('TEST: Waiting for navigation after submit...')
        try {
            await page.waitForURL(/\/questions$/, { timeout: 10000 })
            console.log('TEST: Navigation successful')
        } catch (e) {
            console.log(`TEST: Navigation failed. Current URL: ${page.url()}`)
            // Check if there are validation errors or other UI feedback
            const errorText = await page.locator('.n-form-item-feedback__line').allInnerTexts().catch(() => [])
            console.log('TEST: Validation errors:', errorText)
            const toastMessage = await page.locator('.n-message__content').allInnerTexts().catch(() => [])
            console.log('TEST: Toast messages:', toastMessage)
            throw e
        }
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
