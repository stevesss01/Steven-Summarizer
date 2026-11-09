export type AnalysisMode = "general" | "resume" | "research";

export interface ModeOption {
  id: AnalysisMode;
  title: string;
  description: string;
  icon: string;
}

export const MODES: ModeOption[] = [
  {
    id: "general",
    title: "General Summary",
    description: "Executive brief for reports, notes and articles",
    icon: "📄",
  },
  {
    id: "resume",
    title: "Resume Review",
    description: "ATS score, strengths, gaps and a hiring verdict",
    icon: "🧑‍💼",
  },
  {
    id: "research",
    title: "Research Paper",
    description: "Problem, method, findings and viva questions",
    icon: "🔬",
  },
];

export const MAX_UPLOAD_MB = 10;
