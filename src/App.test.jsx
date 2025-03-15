import { test, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

global.fetch = vi.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ data: { bookings: [] } })
  })
);

test('App renders title', () => {
  render(<App />);
  expect(screen.getByText('Technician Booking System')).toBeDefined();
});
