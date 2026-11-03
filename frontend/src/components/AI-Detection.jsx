import { useState } from "react";
import SearchIcon from "@mui/icons-material/SearchRounded"
import { TextField, Button, CircularProgress, Alert, Box } from "@mui/material";

export default function AIDetection() {
  const [text, setText] = useState("");
  const [status, setStatus] = useState("typing")
  const [formError, setFormError] = useState(null)

  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;


  async function handleSubmit(e) {
    e.preventDefault();
    if (wordCount < 50) {
      setFormError(`Please enter at least 50 words (you have ${wordCount}).`);
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
      await submitForm(text);
      setStatus('complete');
    } catch (err) {
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
                onChange={(e) => {setText(e.target.value); setFormError(null); }}
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
          {status === 'complete' && <p>yay it worked</p>}
          {status === 'error' && <Alert severity="error" variant="outlined">Error, Please try again!</Alert>}
        </Box>

      </Box>
    </div>

  );

  function submitForm(text) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        let shouldError = text.includes("blerp")
        if (shouldError) {
          reject(new Error('Please wait before trying again.'));
        } else {
          resolve();
        }
      }, 1500);
    });
  }
}