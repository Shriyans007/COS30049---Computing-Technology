import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import ErrorFallback from './ErrorFallback';
import ErrorPage from './ErrorPage';

describe('error pages', () => {
  it('renders a useful 404 route with a home action', () => {
    render(<MemoryRouter><ErrorPage /></MemoryRouter>);
    expect(screen.getByRole('heading', { name: /page does not exist/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /return to the detector/i })).toHaveAttribute('href', '/');
  });

  it('renders the unexpected-error fallback without a blank page', () => {
    render(<ErrorFallback />);
    expect(screen.getByRole('alert')).toHaveTextContent(/something went wrong/i);
    expect(screen.getByRole('link', { name: /reload the detector/i })).toBeInTheDocument();
  });
});
