import Banner from "../components/Banner.jsx";
import AIDetection from "../components/AI-Detection.jsx";
import SessionHistory from "../components/SessionHistory.jsx";
import { useState } from "react";


export default function Home() {
  const [sessionHistory, setSessionHistory] = useState([])
  function addToSession(entry) {
    setSessionHistory((prev) => [...prev, entry]);
  }
  return (
    <>
      <Banner />
      <AIDetection onResult={addToSession} />
      <SessionHistory history={sessionHistory} />
    </>
  );
}