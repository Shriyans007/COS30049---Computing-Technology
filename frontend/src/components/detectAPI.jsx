const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const API_BASE_URL = configuredBaseUrl.replace(/\/$/, "");
const REQUEST_TIMEOUT_MS = 20_000;

function friendlyMessage(status, fallback) {
    if (status === 429) return "Too many requests. Please wait a moment and try again.";
    if (status === 503) return "The model is currently busy. Please try again shortly.";
    if (status >= 500) return "The analysis service encountered a problem. Please try again.";
    return fallback || "The request could not be completed.";
}

export async function detectText(text) {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/predict`, {
            method: "POST",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ text }),
            signal: controller.signal,
        });

        let payload;
        try {
            payload = await response.json();
        } catch {
            throw new Error("The analysis service returned an unreadable response.");
        }

        if (!response.ok) {
            throw new Error(friendlyMessage(response.status, payload?.error?.message));
        }

        return payload;
    } catch (error) {
        if (error.name === "AbortError") {
            throw new Error("The analysis took too long. Please try again.", { cause: error });
        }
        if (error instanceof TypeError) {
            throw new Error("The analysis service is unavailable. Check that the backend is running.", { cause: error });
        }
        throw error;
    } finally {
        window.clearTimeout(timeoutId);
    }
}
