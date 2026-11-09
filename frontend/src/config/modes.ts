export type AnalysisMode = "general" | "resume" | "research";

export interface ModeOption {
  id: AnalysisMode;
  title: string;
  description: string;
  contextLabel: string;
  contextPlaceholder: string;
}

export const MODES: ModeOption[] = [
  {
    id: "general",
    title: "General Summary",
    description: "Brief with deadlines, risks and next steps",
    contextLabel: "What do you need from this document?",
    contextPlaceholder:
      "e.g. Am I eligible for the scholarship, and what is the deadline?",
  },
  {
    id: "resume",
    title: "Resume Review",
    description: "ATS score, job match and rewritten bullets",
    contextLabel: "Target role or job description",
    contextPlaceholder:
      "e.g. Backend Engineer, or paste the job description to get a match score",
  },
  {
    id: "research",
    title: "Research Paper",
    description: "Plain-language brief and viva Q&A",
    contextLabel: "What is it for?",
    contextPlaceholder: "e.g. Preparing for my project viva next week",
  },
];

export const MAX_UPLOAD_MB = 10;
export const MAX_CONTEXT_CHARS = 4000;
