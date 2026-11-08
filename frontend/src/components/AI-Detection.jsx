import { useState } from "react";
import SearchIcon from "@mui/icons-material/SearchRounded"
import { detectText } from "./detectAPI";
import { TextField, Button, CircularProgress, Alert, Box, Typography, LinearProgress, Chip } from "@mui/material";



export default function AIDetection({ onResult }) {
  const [text, setText] = useState("");
  const [status, setStatus] = useState("typing")
  const [formError, setFormError] = useState(null)
  const [errorMessage, setErrorMessage] = useState("");
  const [result, setResult] = useState(null)

  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;
  const characterCount = text.length;
  const byteCount = new TextEncoder().encode(text).length;
  const sentenceCount = text.trim() ? text.trim().split(/(?<=[.!?])\s+/).filter(Boolean).length : 0;
  const progressId = "ai-probability-label"
  const verdictWording = {
    ai: "Likely AI-written",
    human: "Likely human-written",
  };

  // Validate inputs 
  async function handleSubmit(e) {
    e.preventDefault();

    if (!text.trim()) {
      setFormError("Enter some text before starting the analysis.");
      setStatus('typing');
      return;
    }
    if (characterCount < 20) {
      setFormError(`Please enter at least 20 characters (you have ${characterCount}).`);
      setStatus('typing');
      return;
    }
    if (characterCount > 10000 || byteCount > 40000) {
      setFormError("Text must stay within 10,000 characters and 40,000 UTF-8 bytes.");
      setStatus('typing');
      return;
    }
    if (sentenceCount > 100) {
      setFormError(`Please keep your text to 100 sentences or fewer (you have ${sentenceCount}).`);
      setStatus('typing');
      return;
    }
    setFormError(null);
    setErrorMessage("");
    setResult(null);
    setStatus('processing');
    try {
      const data = await detectText(text);
      setResult(data);
      onResult?.({
        docId: crypto.randomUUID(),
        docPreview: text.trim().slice(0, 40),
        fullText: text.trim(),
        wordCount,
        prediction: data.prediction,
        ai_probability: data.ai_probability,
        confidence: data.confidence,
        confidence_range: data.confidence_range ?? null,
      }, data);
      setStatus('complete');
    } catch (err) {
      setErrorMessage(err.message);
      setStatus('error');
    }

  }

  return (
    <div className="AI-Detection">
      <p id="try-session-button">TRY IT NOW</p>
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

        }} >
          {/* AI Detection Input */}
          <Box component={"form"} id="detection-input" onSubmit={handleSubmit}>
            <div className="input-internal">
              <TextField
                id="text-input"
                multiline
                minRows={8}
                maxRows={16}
                fullWidth
                variant="filled"
                label="Text to analyse"
                slotProps={{ input: { disableUnderline: true }, htmlInput: { "aria-describedby": "text-guidance" }, }}
                placeholder="Paste a paragraph or document here..."
                value={text}
                onChange={(e) => { setText(e.target.value); setFormError(null); setErrorMessage(""); if (status === "error") setStatus("typing"); }}
                error={formError !== null}
                helperText={formError ?? "20–10,000 characters, up to 100 sentences."}
                disabled={status === 'processing'}
                sx={{
                  "& .MuiFilledInput-root": {
                    bgcolor: "#fabeb43a",
                    borderRadius: "1rem",
                    overflow: "hidden",
                    px: 2,
                    pb: 2,
                    pt: "30px",
                    fontSize: "1rem",
                    fontWeight: "normal",
                    color: "#110f0c",
                  }

                }}
              />
            </div>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 2, mt: 2, }}>
              <p id="text-guidance">{characterCount.toLocaleString()} characters · {wordCount.toLocaleString()} words</p>
              <Box sx={{ display: "flex", gap: 1 }}>
                <Button
                  type="button"
                  variant="outlined"
                  disabled={status === 'processing' || text.length === 0}
                  onClick={() => { setText(""); setResult(null); setFormError(null); setErrorMessage(""); setStatus("typing"); }}
                  sx={{ textTransform: "none" }}
                >
                  Clear
                </Button>
                <Button type="submit" variant="contained" color="error" disabled={status === 'processing'} sx={{ textTransform: "none", color: "#3B2A1A" }}>  <SearchIcon />Analyse</Button>
              </Box>
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
          minHeight: { xs: 300 },
          color: "#7A5C3A"
        }}>
          {status === 'typing' && <p>Results Will Appear Here</p>}
          {status === 'processing' && (
            <Box role="status" sx={{ display: "grid", justifyItems: "center", gap: 2 }}>
              <CircularProgress />
              <Typography>Analysing your text…</Typography>
            </Box>
          )}
          {status === 'complete' && (
            <Box className="card-output">
              <Chip label="Analysis complete" color="secondary" size="small"/>
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
              <div className="progress-bar">
                <Typography variant="h3" sx={{ color: "#755637", fontSize: "2.5rem" }}>
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
                {result.confidence_range && (
                  <Typography variant="body2" sx={{ mt: 1, color: "#584028" }}>
                    Sentence range: {Math.round(result.confidence_range.lower * 100)}%–{Math.round(result.confidence_range.upper * 100)}%
                  </Typography>
                )}
                {result.normalisation_applied && (
                  <Typography variant="caption" sx={{ mt: 1, color: "#584028", display: "block" }}>
                    Security normalisation was applied before analysis.
                  </Typography>
                )}
              </div>
            </Box>
          )}
          {status === 'error' && <Alert severity="error" variant="outlined">{errorMessage || "Something went wrong. Please try again."}</Alert>}
        </Box>

      </Box>
    </div >

  );
}
