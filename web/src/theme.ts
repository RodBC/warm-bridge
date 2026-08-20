import { createTheme, alpha } from "@mui/material/styles";

const navy = "#05072e";
const blue = "#007bc0";
const blueLight = "#00a3e0";
const gray = "#606b71";
const grayLight = "#f4f4f4";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: blue,
      light: blueLight,
      dark: navy,
      contrastText: "#ffffff",
    },
    secondary: {
      main: blueLight,
      contrastText: navy,
    },
    background: {
      default: grayLight,
      paper: "#ffffff",
    },
    text: {
      primary: navy,
      secondary: gray,
    },
    divider: alpha(navy, 0.08),
    success: { main: "#1b7a4e" },
    warning: { main: "#c45c26" },
    error: { main: "#b42318" },
    info: { main: blue },
  },
  typography: {
    fontFamily: '"Noto Sans", system-ui, sans-serif',
    h1: { fontWeight: 300, letterSpacing: "-0.02em", fontSize: "2.25rem" },
    h2: { fontWeight: 300, letterSpacing: "-0.01em", fontSize: "1.5rem" },
    h3: { fontWeight: 500, fontSize: "1.1rem" },
    h4: { fontWeight: 600, fontSize: "1rem" },
    overline: {
      fontWeight: 700,
      letterSpacing: "0.2em",
      fontSize: "0.68rem",
      lineHeight: 1.6,
    },
    button: { fontWeight: 600, textTransform: "none" },
    body1: { fontSize: "0.95rem", lineHeight: 1.55 },
    body2: { fontSize: "0.875rem", lineHeight: 1.5 },
  },
  shape: { borderRadius: 4 },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage: `
            radial-gradient(ellipse 900px 480px at 0% -10%, rgba(0,123,192,0.12), transparent 55%),
            radial-gradient(ellipse 700px 400px at 100% 0%, rgba(5,7,46,0.08), transparent 50%),
            linear-gradient(180deg, #f4f4f4 0%, #eef1f4 100%)
          `,
          minHeight: "100vh",
        },
        "#root": { minHeight: "100vh" },
      },
    },
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: { borderRadius: 999, px: 2.5, py: 1 },
        contained: {
          "&.MuiButton-containedPrimary": {
            backgroundColor: blue,
            "&:hover": { backgroundColor: blueLight },
          },
        },
        outlined: {
          borderWidth: 1.5,
          "&:hover": { borderWidth: 1.5 },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          border: `1px solid ${alpha(navy, 0.08)}`,
          boxShadow: "0 1px 2px rgba(5,7,46,0.06)",
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: "none" },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: alpha(navy, 0.92),
          backdropFilter: "blur(10px)",
          boxShadow: "none",
          borderBottom: `1px solid ${alpha("#fff", 0.08)}`,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontWeight: 600, letterSpacing: "0.03em" },
        colorPrimary: {
          backgroundColor: alpha(blue, 0.12),
          color: blue,
        },
      },
    },
    MuiTextField: {
      defaultProps: { size: "small", variant: "outlined" },
    },
    MuiTab: {
      styleOverrides: {
        root: { textTransform: "none", fontWeight: 600, minHeight: 44 },
      },
    },
  },
});
