
export default function ErrorFallback() {
  return (
    <main className="fallback-page" role="alert">
      <p className="error-code">Unexpected error</p>
      <h1>Something went wrong</h1>
      <p>Your text has not been submitted. Reload the application or return to the detector.</p>
      <a href="/" className="fallback-button">Reload the detector</a>
    </main>
  );
}
