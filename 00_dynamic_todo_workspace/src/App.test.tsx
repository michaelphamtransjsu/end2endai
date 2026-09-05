import { render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import App from './App'

afterEach(() => vi.restoreAllMocks())
test('renders the task composer and an empty task list', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify([]), { status: 200, headers: { 'Content-Type': 'application/json' } }))
  render(<App />)
  expect(screen.getByRole('heading', { name: 'Add a task' })).toBeInTheDocument()
  expect(screen.getByLabelText('Task title')).toBeInTheDocument()
  expect(await screen.findByText('No tasks here.')).toBeInTheDocument()
})
