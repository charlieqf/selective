import { test, expect } from '@playwright/test';

test.describe('Image Rotation', () => {
    test.use({ storageState: 'e2e/.auth/testuser.json' });

    test('should rotate image in question detail', async ({ page }) => {
        // Get current user ID from localStorage
        await page.goto('/dashboard');
        const userStr = await page.evaluate(() => localStorage.getItem('user'));
        const currentUser = JSON.parse(userStr);
        const userId = currentUser.id;

        // Mock item API - use demo cloudinary URL that doesn't require config
        // Mock item API 
        await page.route('**/api/items/999', async route => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    json: {
                        id: 999,
                        title: 'Rotation Test Question',
                        subject: 'MATHS',
                        images: [{ url: 'https://res.cloudinary.com/demo/image/upload/sample.jpg', public_id: 'sample', rotation: 0 }],
                        author_id: userId,
                        difficulty: 3,
                        status: 'UNANSWERED',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString()
                    }
                });
            } else {
                await route.continue();
            }
        });
    });

    // Mock rotate API
    await page.route('**/api/items/*/rotate', async route => {
        const method = route.request().method();
        if (method === 'PATCH') {
            const data = route.request().postDataJSON();
            await route.fulfill({
                json: {
                    rotation: data.rotation,
                    image_index: data.image_index,
                    updated_at: new Date().toISOString()
                }
            });
        } else {
            await route.continue();
        }
    });

    // Mock history API - only intercept GET requests  
    await page.route('**/api/items/*/history', async route => {
        if (route.request().method() === 'GET') {
            await route.fulfill({ json: [] });
        } else {
            await route.continue();
        }
    });

    await page.goto('/questions/999');
    await page.waitForSelector('.n-carousel');

    const img = page.locator('.n-carousel img').first();
    await expect(img).toBeVisible();
    const initialSrc = await img.getAttribute('src');

    // Verify rotation buttons are visible
    const rotateRightBtn = page.locator('[data-testid="rotate-right-btn"]');
    await expect(rotateRightBtn).toBeVisible();

    // Click rotate button
    await rotateRightBtn.click();

    // Wait for optimistic update
    await page.waitForTimeout(1000);

    // Verify image URL changed (Cloudinary transformation applied)
    const newSrc = await img.getAttribute('src');
    expect(newSrc).not.toBe(initialSrc);
    expect(newSrc).toMatch(/a_90/); // Cloudinary angle parameter

    // Verify success message
    await expect(page.locator('text=Image rotated')).toBeVisible({ timeout: 5000 });
});
});
