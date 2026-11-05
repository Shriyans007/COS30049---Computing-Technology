
import { Link } from "react-router-dom";

export default function ErrorPage() {
  return (
    <main className="error-page">
      <p className="error-code">404</p>
      <h1>That page does not exist</h1>
      <p>The address may be incorrect, or the page may have moved.</p>
      <Link to="/" className="fallback-button">Return to the detector</Link>
    </main>
  );
}
