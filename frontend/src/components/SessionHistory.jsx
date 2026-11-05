import { useState } from "react";
import { Box, Typography } from "@mui/material";

const Ranges = [
    { key: "strong", min: 0.9, bg: "#F28482", label: "Strong AI Likelihood" },
    { key: "moderate", min: 0.7, bg: "#F6BD60", label: "Moderate AI Likelihood" },
    { key: "low", min: 0.5, bg: "#84A59D", label: "Low AI Likelihood" },
]

const HumanCategory = {bg: "#F5CAC3", label: "Labelled Human" };

function getRange(entry) {
    if (entry.prediction !== "ai") return null;
    return (
        Ranges.find((r) => entry.ai_probability >= r.min) ??
        Ranges[Ranges.length - 1]
    )
}

export default function SessionHistory({ history }) {
    const [selectedId, setSelectedId] = useState(null)
    const selected = history.find((entry) => entry.docId === selectedId) ?? null;
    return (
        <div className="Session-History">
            <p id="try-session-button">SESSION HISTORY</p>
            
            <Box aria-live="polite" sx={{
                bgcolor: '#FFFF',
                borderRadius: "1rem",
                p: 2.5,
                width: "100%",
                minHeight: { xs: 300 },
                color: "#7A5C3A"
            }}>
                <Typography variant="h4" component="h3" sx={{color: "#755637", fontWeight: "bold", fontFamily:'Fraunces'}}>Review Previous Entries.</Typography>
                {history.length === 0 && <p>No checks yet!</p>}

                {history.map((entry, index) => {
                    const finalPercentage = Math.round(entry.ai_probability * 100);
                    const isSelected = entry.docId === selectedId;
                    const range = getRange(entry);
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
                                    bgcolor: range?.bg ?? HumanCategory.bg,
                                    borderRadius: "8px",
                                }} />
                            </Box>
                        </Box>
                    );
                })}
                <Box aria-live="polite" sx={{ mt: 2, p: 2, borderRadius: "1rem", bgcolor: "#fabeb43a", minHeight: 80 }}>
                    {selected ? (
                        <>
                            <Typography variant="subtitle2" component="h3" sx={{ fontWeight: "bold" }}>
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
