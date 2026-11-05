
export default function ErrorFallback() {
return (
  <main className="fallback-page">
    <h1>Hi there</h1>
    <p>Try reloading this page or press the button to retun to the home page</p>
    <a href="/" className="fallback-button">Return to home</a>
  </main>
)
}