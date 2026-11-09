export default function Banner() {
  return (
    <div className="banner">
      <h1>ag<span className="italic-words">ai</span>nster</h1>
      <h1 id="againstai">Against AI. <span id="forever">Forever.</span></h1> 
      <p>Paste text to receive an AI-likelihood estimate, sentence-level explanation and session comparison.</p>

      <div className="anchor-buttons">
        <a href="#ai-detection" className="text-check" id="ab-1">Check your text</a>
      </div>

      <div className="bubbles">
        <p id="bb-1"><span className="bubblebold">2</span>&nbsp;TRAINED MODELS</p>
        <p id="bb-2"><span className="bubblebold">100</span>&nbsp;SENTENCE LIMIT</p>
        <p id="bb-3"><span className="bubblebold">0</span>&nbsp;TEXTS STORED</p>
      </div>
    </div>
  );
}
