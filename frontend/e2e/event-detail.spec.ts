import { expect, test } from '@playwright/test'

test('navigates from home to event detail', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('link', { name: /Indie Rock Night at Metro/i }).click()

  await expect(page).toHaveURL(/\/events\/mock-001$/)
  await expect(page.getByRole('heading', { level: 1, name: 'Indie Rock Night at Metro' })).toBeVisible()
})
