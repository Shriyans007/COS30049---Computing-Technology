import Banner from "../components/Banner.jsx";
import AIDetection from "../components/AI-Detection.jsx";
import SessionHistory from "../components/SessionHistory.jsx";
import SentenceHighlight from "../components/SentenceHighlight.jsx";
import { useState } from "react";

export default function Home() {
  const [sessionHistory, setSessionHistory] = useState([]);
  const [latestResult, setLatestResult] = useState(null);

  function addToSession(entry, data) {
    setSessionHistory((prev) => [...prev, entry]);
    setLatestResult(data);
  }

  return (
    <>
      <Banner />
      <AIDetection onResult={addToSession} />
      <div className="results-row">
        {latestResult?.sentence_results && (
          <div className="sentence-area">
           <p id="try-session-button">OVERVIEW</p>
          <div className="sentence-by-sentence" aria-live="polite">
            <SentenceHighlight sentences={latestResult.sentence_results} />
            </div>
          </div>
        )}
        <SessionHistory history={sessionHistory} />
      </div>
    </>
  );
}