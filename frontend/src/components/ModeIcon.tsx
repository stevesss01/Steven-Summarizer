import type { AnalysisMode } from "../config/modes";

const PATHS: Record<AnalysisMode, string[]> = {
  // Document with text lines
  general: [
    "M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z",
    "M14 3v5h5",
    "M9 13h6",
    "M9 17h4",
  ],
  // Person with a clipboard-style frame
  resume: [
    "M16 4h1a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1",
    "M9 3h6v3H9z",
    "M12 13a2 2 0 1 0 0-4 2 2 0 0 0 0 4z",
    "M8.5 18a3.5 3.5 0 0 1 7 0",
  ],
  // Flask
  research: [
    "M9 3h6",
    "M10 3v6l-5 9a2 2 0 0 0 1.7 3h10.6a2 2 0 0 0 1.7-3l-5-9V3",
    "M7.5 15h9",
  ],
};

export default function ModeIcon({ mode }: { mode: AnalysisMode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width="22"
      height="22"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {PATHS[mode].map((d) => (
        <path key={d} d={d} />
      ))}
    </svg>
  );
}
