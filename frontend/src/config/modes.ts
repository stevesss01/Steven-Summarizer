export type AnalysisMode = "general" | "resume" | "research";

export interface ModeOption {
  id: AnalysisMode;
  title: string;
  description: string;
}

export const MODES: ModeOption[] = [
  {
    id: "general",
    title: "General Summary",
    description: "Executive brief for reports, notes and articles",
  },
  {
    id: "resume",
    title: "Resume Review",
    description: "ATS score, strengths, gaps and a hiring verdict",
  },
  {
    id: "research",
    title: "Research Paper",
    description: "Problem, method, findings and viva questions",
  },
];

export const MAX_UPLOAD_MB = 10;
