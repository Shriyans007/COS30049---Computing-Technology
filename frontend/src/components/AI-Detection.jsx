import { useState } from "react";

export default function AIDetection() {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault(); 
  };

  return (
    <div className="AI-Detection">
      <h5 id="trybutton">TRY IT NOW</h5>
      <div id="ai-detection">
        <h2>Drop your text in.</h2>
      </div>

      {/* AI Detection Input */}
      <form id="detection-input" onSubmit={handleSubmit}>
        <div className="input-internal">
          <textarea
            id="text-input"
            rows={6}
            placeholder="Input Text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        <button type="submit">Analyze</button>
      </form>

      {/* AI Detection Output */}
    </div>
  );
}