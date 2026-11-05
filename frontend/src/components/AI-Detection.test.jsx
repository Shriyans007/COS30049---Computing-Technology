import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import AIDetection from './AI-Detection';
import { detectText } from './detectAPI';

vi.mock('./detectAPI', () => ({ detectText: vi.fn() }));

const response = {
  prediction: 'ai',
  ai_probability: 0.91,
  confidence: 0.91,
  confidence_range: { lower: 0.84, upper: 0.96, method: 'bootstrap' },
  sentence_results: [{ text: 'A test sentence.', label: 'ai', ai_probability: 0.93 }],
  normalisation_applied: false,
};

describe('AIDetection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal('crypto', { randomUUID: () => 'test-id' });
  });

  it('validates empty and short input before calling the API', async () => {
    const user = userEvent.setup();
    render(<AIDetection />);

    await user.click(screen.getByRole('button', { name: /analyse/i }));
    expect(screen.getByText(/enter some text/i)).toBeInTheDocument();
    expect(detectText).not.toHaveBeenCalled();

    await user.type(screen.getByLabelText(/text to analyse/i), 'too short');
    await user.click(screen.getByRole('button', { name: /analyse/i }));
    expect(screen.getByText(/at least 20 characters/i)).toBeInTheDocument();
    expect(detectText).not.toHaveBeenCalled();
  });

  it('shows loading and then renders the prominent result', async () => {
    let resolveRequest;
    detectText.mockReturnValue(new Promise((resolve) => { resolveRequest = resolve; }));
    const onResult = vi.fn();
    const user = userEvent.setup();
    render(<AIDetection onResult={onResult} />);

    await user.type(screen.getByLabelText(/text to analyse/i), 'This input is definitely longer than twenty characters.');
    await user.click(screen.getByRole('button', { name: /analyse/i }));
    expect(screen.getByText(/analysing your text/i)).toBeInTheDocument();

    resolveRequest(response);
    expect(await screen.findByText('Likely AI-written')).toBeInTheDocument();
    expect(screen.getAllByText('91%').length).toBeGreaterThan(0);
    expect(onResult).toHaveBeenCalled();
  });

  it('renders a readable API failure and allows another attempt', async () => {
    detectText.mockRejectedValue(new Error('The model is currently busy. Please try again shortly.'));
    render(<AIDetection />);

    fireEvent.change(screen.getByLabelText(/text to analyse/i), {
      target: { value: 'This input is definitely longer than twenty characters.' },
    });
    fireEvent.click(screen.getByRole('button', { name: /analyse/i }));

    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('currently busy'));
  });
});
