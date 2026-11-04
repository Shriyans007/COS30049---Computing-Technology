import { useState } from "react";
import { Box, Typography, Button } from "@mui/material";

export default function SessionHistory({ history }) {
    const [selectedId, setSelectedId] = useState(null)
    const selected = history.find((entry) => entry.docId === selectedId) ?? null;
    return (
        <div className="Session-History">
            <Box aria-live="polite" sx={{
                bgcolor: '#FFFF',
                borderRadius: "1rem",
                p: 2.5,
                width: "100%",
                maxWidth: 1024,
                mx: "auto",
                minHeight: { xs: 300 },
                color: "#7A5C3A"
            }}>
                <Typography variant="h5" component="h3" sx={{color: "#F28482", fontWeight: "bold", fontFamily:'Fraunces'}}>Session history</Typography>
                {history.length === 0 && <p>No checks yet!</p>}

                {history.map((entry, index) => {
                    const finalPercentage = Math.round(entry.ai_probability * 100);
                    const isSelected = entry.docId === selectedId;

                    return (
                        <Box
                            key={entry.docId}
                            component="button"
                            type="button"
                            onClick={() => setSelectedId(entry.docId)}
                            aria-pressed={isSelected}
                            sx={{
                                display: "block",
                                width: "100%",
                                textAlign: "left",
                                font: "inherit",
                                color: "inherit",
                                bgcolor: isSelected ? "#fabeb43a" : "transparent",
                                border: "2px solid",
                                borderColor: isSelected ? "#7A5C3A" : "transparent",
                                borderRadius: "8px",
                                p: 1,
                                mb: 1,
                                cursor: "pointer",
                            }}
                        >
                            <Typography variant="body2" sx={{ fontWeight: "bold" }}>
                                Check {index + 1}: {finalPercentage}% AI probability
                            </Typography>

                            {/* grey track */}
                            <Box sx={{ position: "relative", height: 16, bgcolor: "#f1ece6", borderRadius: "8px", mt: 0.5 }}>
                                {/* coloured bar */}
                                <Box sx={{
                                    position: "absolute",
                                    top: 0,
                                    left: 0,
                                    bottom: 0,
                                    width: `${finalPercentage}%`,
                                    bgcolor: entry.prediction === "ai" ? "#F28482" : "#84A59D",
                                    borderRadius: "8px",
                                }} />
                            </Box>
                        </Box>
                    );
                })}
                <Box aria-live="polite" sx={{ mt: 2, p: 2, borderRadius: "1rem", bgcolor: "#fabeb43a", minHeight: 80 }}>
                    {selected ? (
                        <>
                            <Typography variant="subtitle2" sx={{ fontWeight: "bold" }}>
                                {selected.prediction === "ai" ? "Labelled AI" : "Labelled Human"}
                            </Typography>
                            <Typography variant="body2">
                                {Math.round(selected.ai_probability * 100)}% AI probability ·{" "}
                                {Math.round(selected.confidence * 100)}% confidence
                            </Typography>
                            {selected.confidence_range && (
                                <Typography variant="body2">
                                    Range: {Math.round(selected.confidence_range.lower * 100)}% to{" "}
                                    {Math.round(selected.confidence_range.upper * 100)}%
                                </Typography>
                            )}
                            <Typography variant="body2">{selected.wordCount} words</Typography>
                            <Typography variant="body2" sx={{ fontStyle: "italic", mt: 1 }}>
                                "{selected.fullText}"
                            </Typography>
                        </>
                    ) : (
                        <Typography variant="body2">Select a check to see its details.</Typography>
                    )}
                </Box>
            </Box>
        </div>
    )
}