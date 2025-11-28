import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
    testDir: './e2e',
    timeout: 30000,
    retries: 1,
    workers: 1, // Run tests serially to avoid DB conflicts
    globalSetup: './e2e/global.setup.js',

    use: {
        baseURL: 'http://localhost:5173',
        storageState: './e2e/.auth/testuser.json',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
        trace: 'retain-on-failure',
    },

    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
    ],

    // Start dev server before running tests
    webServer: {
        command: 'npm run dev',
        port: 5173,
        reuseExistingServer: !process.env.CI,
        timeout: 120000,
    },
})
