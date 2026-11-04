import { Tooltip, Box, Typography, Zoom, Chip, Button } from "@mui/material";
import { Fragment, useState } from "react";

const Ranges = [
    { key: "strong", min: 0.9, bg: "#F2848277", label: "Strong AI Likelihood" },
    { key: "moderate", min: 0.7, bg: "#F6BD6077", label: "Moderate AI Likelihood" },
    { key: "low", min: 0.5, bg: "#84A59D77", label: "Low AI Likelihood" },
]

const HumanCategory = { key: "human", bg: "transparent", label: "Labelled Human" };
const Categories = [...Ranges, HumanCategory];

const verdictWording = {
    ai: "Labelled AI",
    human: "Labelled Human",
};


function getRange(sentence) {
    if (sentence.label !== "ai") return null;
    return (
        Ranges.find((r) => sentence.ai_probability >= r.min) ??
        Ranges[Ranges.length - 1]
    )
}

function getDetails(sentence) {
    const range = getRange(sentence);
    return {
        range,
        categoryKey: range ? range.key : "human",
        verdict: verdictWording[sentence.label] ?? "Label unavailable",
        finalPercentage: Math.round(sentence.ai_probability * 100),
    };
}

export default function SentenceHighlight({ sentences }) {
    const [activeFilter, setActiveFilter] = useState(null);


    function toggleFilter(key) {
        if (activeFilter === key) {
            setActiveFilter(null);
        }
        else {
            setActiveFilter(key);
        }
    }

    return (
        <Box sx={{}}>
            <Typography variant="h3" component="h3" sx={{ color: "#F6BD60", fontSize: "2.5rem" }}>Sentence-by-Sentence Overview</Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
                Hover or focus for details, or use the buttons to filter by type.
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 2, justifyContent: "center" }}>
                {Categories.map((category) => {
                    const active = activeFilter === category.key;
                    return (
                        <Chip
                            key={category.key}
                            label={category.label}
                            onClick={() => toggleFilter(category.key)}
                            aria-pressed={active}
                            variant={active ? "filled" : "outlined"}
                            icon={
                                <Box sx={{
                                    width: 14,
                                    height: 14,
                                    bgcolor: category.bg,
                                    borderRadius: 2,
                                    ml: "10px !important",
                                    border: "1px solid #7A5C3A",
                                }} />
                            }
                            sx={{
                                fontWeight: active ? "bold" : "normal",
                            }}
                        />
                    );
                })}
                {activeFilter !== null && (
                    <Button size="small" onClick={() => setActiveFilter(null)}>Show all</Button>
                )}
            </Box>
            <p>
                {sentences.map((sentence, index) => {
                    const { range, categoryKey, verdict, finalPercentage } = getDetails(sentence);
                    const isDimmed = activeFilter !== null && activeFilter !== categoryKey;
                    const tooltipContent = (
                        <Box sx={{ bgcolor: "#84A59D", color: "#F7EDE2" }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: "bold" }}> {verdict} </Typography>
                            <Typography variant="caption" sx={{ display: "block" }}>  {finalPercentage}% AI probability </Typography>
                            {range && (
                                <Typography variant="caption" sx={{ display: "block" }}>
                                    {range.label}
                                </Typography>
                            )}
                        </Box>
                    );
                    return (
                        <Fragment key={index}>
                            <Tooltip arrow
                                slots={{ transition: Zoom, }}
                                slotProps={{
                                    tooltip: { sx: { bgcolor: "#84A59D", color: "#F7EDE2", padding: "1.5rem" }, },
                                    arrow: { sx: { color: "#84A59D" }, },
                                }}
                                title={tooltipContent}>
                                <Box component="span" 
                                tabIndex={0} sx={{
                                    display: "inline-block",
                                    backgroundColor: range ? range.bg : "transparent",
                                    borderRadius: "4px",
                                    padding: "0 2px",
                                    cursor: "default",
                                    opacity: isDimmed ? 0.3 : 1,
                                    transition: "opacity 0.2s",
                                }}>
                                    {sentence.text}
                                </Box>
                            </Tooltip>{" "}
                        </Fragment>
                    );
                })}
            </p>
        </Box>
    );
}