import { render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import App from './App'

afterEach(() => {
  vi.unstubAllGlobals()
})

test('shows "API ok" when the health check succeeds', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(new Response(JSON.stringify({ ok: true }), { status: 200 })),
  )
  render(<App />)
  expect(await screen.findByText('API ok')).toBeInTheDocument()
})

test('shows "API down" when the health check fails', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
  render(<App />)
  expect(await screen.findByText('API down')).toBeInTheDocument()
})
