import { expect, test } from '@playwright/test'

test('home page displays event feed', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'Explore' })).toBeVisible()
  await expect(page.getByText('Indie Rock Night at Metro')).toBeVisible()
})
