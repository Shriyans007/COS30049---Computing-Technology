export default function Banner() {
  return (
    <div className="banner">
      <h1>Know if it&apos;s&nbsp;<span className="italic-words">real</span></h1>
      <h1 id="instantly">Instantly.</h1>
      <p>Paste any text and find out if a human or AI wrote it — in under 3 seconds.</p>

      <div className="anchor-buttons">
        <a href="#ai-detection" className="text-check" id="ab-1">Check your text</a>
        <a href="#ai-detection" className="how-it-works" id="ab-2">See how it works</a>
      </div>

      <div className="bubbles">
        <p id="bb-1"><span className="bubblebold">85%</span>&nbsp;ACCURACY</p>
        <p id="bb-2"><span className="bubblebold">10+</span>&nbsp;DOCS SCANNED</p>
        <p id="bb-3"><span className="bubblebold">{"<3"}</span>&nbsp;AVG. TIME</p>
      </div>
    </div>
  );
}