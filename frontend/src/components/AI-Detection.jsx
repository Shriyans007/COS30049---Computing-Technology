import { useState } from "react";
import SearchIcon from "@mui/icons-material/SearchRounded"
import SentenceHighlight from "./SentenceHighlight";
import { detectText } from "./detectAPI";
import { TextField, Button, CircularProgress, Alert, Box, Typography, LinearProgress } from "@mui/material";



export default function AIDetection({ onResult }) {
  const [text, setText] = useState("");
  const [status, setStatus] = useState("typing")
  const [formError, setFormError] = useState(null)
  const [errorMessage, setErrorMessage] = useState("");
  const [result, setResult] = useState(null)

  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;
  const progressId = "ai-probability-label"
  const verdictWording = {
    ai: "Likely AI-written",
    human: "Likely human-written",
  };

  async function handleSubmit(e) {
    e.preventDefault();

    if (wordCount < 20) {
      setFormError(`Please enter at least 20 words (you have ${wordCount}).`);
      setStatus('typing');
      return;
    }
    if (wordCount > 10000) {
      setFormError(`Please keep your text under 10,000 words (you have ${wordCount}).`);
      setStatus('typing');
      return;
    }
    setFormError(null);
    setStatus('processing');
    try {
      const data = await detectText(text);
      setResult(data);
      onResult?.({
        docId: crypto.randomUUID(),
        timestamp: Date.now(),
        docPreview: text.trim().slice(0, 40), 
        fullText: text.trim(),
        wordCount,
        prediction: data.prediction,
        ai_probability: data.ai_probability,
        confidence: data.confidence,
        confidence_range: data.confidence_range ?? null,
      });
      setStatus('complete');
    } catch (err) {
      setErrorMessage(err.message);
      setStatus('error');
    }

  }

  return (
    <div className="AI-Detection">
      <h5 id="trybutton">TRY IT NOW</h5>
      <div id="ai-detection">
        <h2>Drop your text in.</h2>
      </div>
      <Box sx={{
        display: "flex",
        flexDirection: { xs: "column", md: "row" },
        gap: 3,
        width: "100%",
        alignItems: "stretch",
        justifyContent: "center",
        minHeight: "100%"
      }}>
        <Box sx={{
          bgcolor: '#FFFF',
          borderRadius: "1rem",
          p: 2.5,
          width: "100%",
          maxWidth: 500,

        }} >
          {/* AI Detection Input */}
          <Box component={"form"} id="detection-input" onSubmit={handleSubmit}>
            <div className="input-internal">
              <TextField
                id="text-input"
                multiline
                minRows={8}
                fullWidth
                variant="filled"
                slotProps={{ input: { disableUnderline: true }, htmlInput: { "aria-label": "Text to analyse" }, }}
                placeholder="Input Text here..."
                value={text}
                onChange={(e) => { setText(e.target.value); setFormError(null); }}
                error={formError !== null}
                helperText={formError}
                disabled={status === 'processing'}
                sx={{
                  "& .MuiFilledInput-root": {
                    bgcolor: "#fabeb43a",
                    borderRadius: "1rem",
                    overflow: "hidden",
                    p: 2,
                    fontSize: "1rem",
                    fontWeight: "normal",
                    color: "#110f0c",
                  }

                }}
              />
            </div>
            <Box sx={{ display: "flex", justifyContent: "space-between", gap: 2, mt: 2, }}>
              <p id="wordcount">{wordCount} words</p>
              <Button type="submit" variant="contained" color="error" disabled={status === 'processing'} sx={{ textTransform: "none", }}>  <SearchIcon></SearchIcon>Analyze</Button>
            </Box>
          </Box>
        </Box>
        {/* AI Detection Output */}
        <Box aria-live="polite" sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: "center",
          bgcolor: '#FFFF',
          borderRadius: "1rem",
          p: 2.5,
          width: "100%",
          maxWidth: 500,
          minHeight: { xs: 300 },
          color: "#7A5C3A"
        }}>
          {status === 'typing' && <p>Results Will Appear Here</p>}
          {status === 'processing' && <CircularProgress />}
          {status === 'complete' && (
            <Box className="card-output">
              <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                {/* Confidence bar */}
                <CircularProgress variant="determinate" size={100} value={Math.round(result.confidence * 100)} />
                <Box id="progress-percent"
                  sx={{
                    top: 0,
                    left: 0,
                    bottom: 0,
                    right: 0,
                    position: 'absolute',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Typography
                    variant="h4"
                    component="div"
                    sx={{ color: "#7A5C3A", fontSize: "1.5rem" }}
                  >{`${Math.round(result.confidence * 100)}%`}</Typography>

                </Box>
              </Box>
              <Typography>Confidence</Typography>
              <Typography variant="h3" sx={{ color: "#F6BD60", fontSize: "2.5rem" }}>
                {verdictWording[result.prediction] ?? "Results unavailable :("}
              </Typography>
              <Typography id={progressId} variant="body2" color="text.secondary">
                AI Probability
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%' }}>

                {/* AI-probability bar */}
                <Box sx={{ width: '50%', mr: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={Math.round(result.ai_probability * 100)}
                    aria-labelledby={progressId}
                    color="secondary"
                    sx={{
                      height: 12,
                      borderRadius: 6,
                      "& .MuiLinearProgress-bar": { borderRadius: 6 },
                    }}
                  />
                </Box>
                <Box sx={{ minWidth: 35 }}>
                  <Typography variant="body2" sx={{ color: 'secondary' }}>
                    {`${Math.round(result.ai_probability * 100)}%`}
                  </Typography>
                </Box>

              </Box>
            </Box>
          )}
          {status === 'error' && <Alert severity="error" variant="outlined">{errorMessage || "Something went wrong. Please try again."}</Alert>}
        </Box>

      </Box>
      {status === 'complete' && (
        // Sentence by sentence output
        <Box className="sentence-by-sentence" aria-live="polite" sx={{
          bgcolor: '#FFFF',
          borderRadius: "1rem",
          p: 2.5,
          width: "100%",
          maxWidth: 500,
          minHeight: { xs: 300 },
          color: "#7A5C3A"
        }}>
          <SentenceHighlight sentences={result.sentence_results} />
        </Box>)}

    </div>

  );
}