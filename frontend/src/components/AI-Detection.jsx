import { useState } from "react";
import SearchIcon from "@mui/icons-material/SearchRounded"
import { TextField, Button, CircularProgress, Alert, Box } from "@mui/material";

export default function AIDetection() {
  const [text, setText] = useState("");

   const wordCount = text.trim().split(/\s+/).filter(Boolean).length;

  const handleSubmit = (e) => {
    e.preventDefault();
  };

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
                slotProps={{ input: { disableUnderline: true } }}
                placeholder="Input Text here..."
                value={text}
                onChange={(e) => setText(e.target.value)}
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
              <Button type="submit" variant="contained" color="error" sx={{ textTransform: "none", }}>  <SearchIcon></SearchIcon>Analyze</Button>
                
            </Box>

              <Box sx={{ display: "flex", justifyContent: "flex-start", gap: 2, mt: 2, }}>
                
            </Box>

          </Box>
        </Box>
        {/* AI Detection Output */}
        <Box sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: "center",
          bgcolor: '#FFFF',
          borderRadius: "1rem",
          p: 2.5,
          width: "100%",
          maxWidth: 500,
          minHeight: {xs: 300},
          color: "#7A5C3A"
        }}>

          <p>Results Will Appear Here</p>
        </Box>

      </Box>
    </div>
  );
}