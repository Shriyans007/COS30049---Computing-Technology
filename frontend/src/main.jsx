import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { ErrorBoundary } from "react-error-boundary";
import { ThemeProvider } from "@mui/material/styles";
import { StyledEngineProvider } from "@mui/material/styles";
import App from "./App.jsx";
import ErrorFallback from "./pages/ErrorFallback.jsx";
import theme from "./theme.jsx";
import "./styles.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <StyledEngineProvider injectFirst>
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          <App />
        </ErrorBoundary>
      </ThemeProvider>
    </BrowserRouter>
    </StyledEngineProvider>
  </StrictMode>
);