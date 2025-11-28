const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext({
        storageState: 'e2e/.auth/testuser.json',
        baseURL: 'http://localhost:5173'
    });
    const page = await context.newPage();

    try {
        console.log('Navigating to /questions');
        await page.goto('/questions');
        await page.waitForURL(/\/questions$/, { timeout: 10000 });
        console.log('Navigated to /questions');

        console.log('Waiting for cards');
        await page.waitForSelector('.card, text=No questions found', { timeout: 10000 });

        const cardCount = await page.locator('.card').count();
        console.log(`Found ${cardCount} cards`);

        if (cardCount > 0) {
            console.log('Clicking first card');
            await page.locator('.card').first().click();
            await page.waitForURL(/\/questions\/\d+/, { timeout: 10000 });
            console.log('Navigated to detail page');

            console.log('Waiting for loading to finish');
            await page.waitForSelector('h1', { timeout: 10000 });

            console.log('Checking content');
            const content = await page.content();
            console.log('Page title:', await page.title());
            console.log('H1:', await page.locator('h1').innerText());

            const bodyText = await page.innerText('body');
            console.log('Body text contains MATHS?', /MATHS|READING|WRITING/.test(bodyText));
            console.log('Body text contains star?', bodyText.includes('⭐'));
        } else {
            console.log('No cards found');
        }

    } catch (e) {
        console.error('Error:', e);
    } finally {
        await browser.close();
    }
})();
