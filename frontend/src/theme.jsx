import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: { main: "#F6BD60", contrastText: "#3B2A1A" },
    secondary: { main: "#84A59D", contrastText: "#3B2A1A" },
    error: { main: "#F28482", contrastText: "#3B2A1A" },
    text: { primary: "#3B2A1A", secondary: "#F7EDE2" },
    background: { default: "#F7EDE2", paper: "#FFFFFF" },
  },
  typography: {
    fontFamily: "'Plus Jakarta Sans', sans-serif",
    h1: { fontFamily: "'Fraunces', serif", fontWeight: 900 },
    h2: { fontFamily: "'Fraunces', serif", fontWeight: 900 },
    h3: { fontFamily: "'Fraunces', serif", fontWeight: 900 },
  },
  shape: { borderRadius: 24 },
});

export default theme;