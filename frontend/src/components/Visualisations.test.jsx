import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import SentenceHighlight from './SentenceHighlight';
import SessionHistory from './SessionHistory';

describe('result visualisations', () => {
  it('filters sentence likelihood categories with keyboard-operable controls', async () => {
    const user = userEvent.setup();
    render(
      <SentenceHighlight
        sentences={[
          { text: 'Strong sentence.', label: 'ai', ai_probability: 0.95 },
          { text: 'Human sentence.', label: 'human', ai_probability: 0.12 },
        ]}
      />,
    );

    await user.click(screen.getByRole('button', { name: /strong ai likelihood/i }));
    expect(screen.getByText('Strong sentence.')).toHaveStyle({ opacity: '1' });
    expect(screen.getByText('Human sentence.')).toHaveStyle({ opacity: '0.3' });
  });

  it('selects a session bar for details and clears history', async () => {
    const user = userEvent.setup();
    const onClear = vi.fn();
    render(
      <SessionHistory
        onClear={onClear}
        history={[
          {
            docId: 'one',
            fullText: 'Example analysed text.',
            wordCount: 3,
            prediction: 'ai',
            ai_probability: 0.82,
            confidence: 0.82,
            confidence_range: null,
          },
        ]}
      />,
    );

    await user.click(screen.getByRole('button', { name: /check 1/i }));
    expect(screen.getByText('Labelled AI')).toBeInTheDocument();
    expect(screen.getAllByText(/82% AI probability/i).length).toBeGreaterThan(0);

    await user.click(screen.getByRole('button', { name: /clear history/i }));
    expect(onClear).toHaveBeenCalledOnce();
  });
});
