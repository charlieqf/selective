import { test as base, expect } from '@playwright/test'
import axios from 'axios'

const API_BASE = process.env.API_BASE || 'http://localhost:5000'

async function ensureTestUser() {
    try {
        await axios.post(`${API_BASE}/api/auth/register`, {
            username: 'testuser',
            email: 'testuser@example.com',
            password: 'password',
            role: 'student'
        })
    } catch (error) {
        if (error.response?.status !== 409) {
            throw error
        }
    }
}

// Extend base test with fixtures
export const test = base.extend({
    // Seed data fixture - ensures at least one question exists
    seedData: async ({ }, use) => {
        await ensureTestUser()
        // Get token from localStorage via page evaluation would be better,
        // but since we're in a fixture without a page, login via API
        const loginResponse = await axios.post(`${API_BASE}/api/auth/login`, {
            username: 'testuser',
            password: 'password'
        })
        const token = loginResponse.data.token

        // Check if any items exist
        const itemsResponse = await axios.get(`${API_BASE}/api/items`, {
            headers: { Authorization: `Bearer ${token}` }
        })

        let createdItems = []

        // If no items exist, create some test items
        if (itemsResponse.data.items.length === 0) {
            const subjects = ['MATHS', 'READING', 'WRITING']
            const difficulties = [1, 2, 3, 4, 5]

            for (let i = 0; i < 3; i++) {
                const itemData = {
                    subject: subjects[i % subjects.length],
                    difficulty: difficulties[i % difficulties.length],
                    title: `Test Question ${i + 1}`,
                    content_text: `This is test question ${i + 1}`,
                    images: []
                }

                const createResponse = await axios.post(
                    `${API_BASE}/api/items`,
                    itemData,
                    { headers: { Authorization: `Bearer ${token}` } }
                )

                createdItems.push(createResponse.data.id)
            }
        }

        // Provide cleanup function
        await use()

        // Cleanup created items after the test completes
        for (const itemId of createdItems) {
            try {
                await axios.delete(`${API_BASE}/api/items/${itemId}`, {
                    headers: { Authorization: `Bearer ${token}` }
                })
            } catch (e) {
                // Already deleted or error - ignore
            }
        }
    }
})

export { expect }
