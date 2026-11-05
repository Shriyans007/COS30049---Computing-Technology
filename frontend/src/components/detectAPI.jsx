// CONNECT API HERE ! :D 
// detectText(text) function must: resolve with the result object :P
// reject with an error message that is readable
//All the mock data can be deleted :D



export async function detectText(text) {
    return submitForm(text);
}
function submitForm(text) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (text.includes("blerp")) {
                reject(new Error('Please wait before trying again.'));
            } else if (text.includes("zoop")) {
                resolve({
                    prediction: "human", ai_probability: 0.09, confidence: 0.91, confidence_range: { lower: 0.04, upper: 0.16, method: "95% bootstrap interval across sentence AI probabilities" }, sentence_results: [{ text: "this is human text", label: "human", ai_probability: 0.03 },
                    { text: "this is human text times two", label: "human", ai_probability: 0.05 }, { text: "this is human text for the third time", label: "human", ai_probability: 0.23 }], normalisation_applied: false
                });
            } else if (text.includes("gromp")) {
                resolve({
                    prediction: "ai", ai_probability: 0.79, confidence: 0.89, sentence_results: [{ text: "hello this is a test", label: "ai", ai_probability: 0.64 },
                    { text: "hello this is the second test", label: "ai", ai_probability: 0.83 }
                    ], normalisation_applied: false
                });
            } else {
                resolve({
                    prediction: "ai", ai_probability: 0.91, confidence: 0.91, confidence_range: { lower: 0.84, upper: 0.96, method: "95% bootstrap interval across sentence AI probabilities" }, sentence_results: [{ text: "Testing testing one two three", label: "ai", ai_probability: 0.93 },
                    { text: "Sentence one, low.", label: "human", ai_probability: 0.33 },
                    { text: "Sentence two, exactly fifty.", label: "ai", ai_probability: 0.5 },
                    { text: "Sentence three, mid teal", label: "ai", ai_probability: 0.6 },
                    { text: "Sentence four, exactly seventy.", label: "ai", ai_probability: 0.7 },
                    { text: "Sentence five, mid yellow.", label: "ai", ai_probability: 0.8 },
                    { text: "Sentence six, exactly ninety.", label: "ai", ai_probability: 0.9 },
                    { text: "Sentence seven, high.", label: "ai", ai_probability: 0.95 },
                    ], normalisation_applied: true
                });
            }
        }, 1500);
    });
}
