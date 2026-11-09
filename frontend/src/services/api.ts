import axios, { AxiosError } from "axios";
import type { AnalysisMode } from "../config/modes";

const API_URL = import.meta.env.VITE_API_URL ?? "https://steven-summarizer.onrender.com";

export const api = axios.create({
  baseURL: API_URL,
  // Long documents are analysed in sections, which can take a few minutes.
  timeout: 240_000,
});

export interface SummaryMeta {
  pages: number;
  pages_analysed: number;
  sections: number;
  truncated: boolean;
  models: string[];
  seconds: number;
}

export interface SummaryResponse {
  summary: string;
  mode: AnalysisMode;
  meta?: SummaryMeta;
}

/** Upload a PDF and receive a markdown analysis. */
export async function summarizeDocument(
  file: File,
  mode: AnalysisMode,
  signal?: AbortSignal,
): Promise<SummaryResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("mode", mode);

  const { data } = await api.post<SummaryResponse>("/summarize", formData, {
    signal,
  });
  return data;
}

/** Ping the API so a sleeping free-tier server starts waking up early. */
export async function pingServer(): Promise<boolean> {
  try {
    await api.get("/health", { timeout: 60_000 });
    return true;
  } catch {
    return false;
  }
}

/** Turn any request error into a short, user-friendly message. */
export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    if (error.code === "ECONNABORTED") {
      return "The request took too long. Please try again.";
    }
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail;
    if (typeof detail === "string") return detail;
    if (!error.response) {
      return "Can't reach the server. Check your connection and try again.";
    }
  }
  return "Something went wrong while analysing the document.";
}
