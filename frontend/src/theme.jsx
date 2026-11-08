import { createTheme } from "@mui/material/styles";

const headingFont = {
  fontFamily: "'Fraunces Variable', serif",
  fontWeight: 900,
};

const theme = createTheme({
  palette: {
    primary: { main: "#F6BD60", contrastText: "#3B2A1A" },
    secondary: { main: "#84A59D", contrastText: "#3B2A1A" },
    error: { main: "#F28482", contrastText: "#3B2A1A" },
    text: { primary: "#3B2A1A", secondary: "#654A32" },
    background: { default: "#F7EDE2", paper: "#FFFFFF" },
  },
  typography: {
    fontFamily: "'Plus Jakarta Sans', sans-serif",
    h1: headingFont,
    h2: headingFont,
    h3: headingFont,
  },
  shape: { borderRadius: 24 },
});

export default theme;