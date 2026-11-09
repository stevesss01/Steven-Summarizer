import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./styles/global.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

// Fade out the boot splash defined in index.html once React has mounted.
const splash = document.getElementById("boot-splash");
if (splash) {
  splash.classList.add("is-hidden");
  splash.addEventListener("transitionend", () => splash.remove(), { once: true });
  window.setTimeout(() => splash.remove(), 800);
}
