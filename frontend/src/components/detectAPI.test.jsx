import { afterEach, describe, expect, it, vi } from 'vitest';

import { detectText } from './detectAPI';

describe('detectText', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('posts the text to the real API contract and returns JSON', async () => {
    const payload = { prediction: 'ai', ai_probability: 0.82, confidence: 0.82 };
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue(payload),
    });

    await expect(detectText('A sufficiently long piece of submitted text.')).resolves.toEqual(payload);
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/predict',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ text: 'A sufficiently long piece of submitted text.' }),
      }),
    );
  });

  it('uses the backend error message for invalid input', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 413,
      json: vi.fn().mockResolvedValue({
        error: { code: 'TEXT_TOO_LARGE', message: 'Text exceeds the allowed size.' },
      }),
    });

    await expect(detectText('oversized')).rejects.toThrow('Text exceeds the allowed size.');
  });

  it('shows a useful server-busy message for 503', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 503,
      json: vi.fn().mockResolvedValue({ error: { code: 'SERVER_BUSY', message: 'busy' } }),
    });

    await expect(detectText('A sufficiently long piece of submitted text.')).rejects.toThrow(
      'The model is currently busy',
    );
  });
});
