import { useCallback, useRef, useState } from "react";
import type { AnalysisMode } from "../config/modes";
import { getErrorMessage, summarizeDocument } from "../services/api";

export type RequestState = "idle" | "loading" | "success" | "error";

export function useSummarize() {
  const [state, setState] = useState<RequestState>("idle");
  const [summary, setSummary] = useState("");
  const [error, setError] = useState<string | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const run = useCallback(async (file: File, mode: AnalysisMode) => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    setState("loading");
    setError(null);
    setSummary("");

    try {
      const result = await summarizeDocument(file, mode, controller.signal);
      setSummary(result.summary);
      setState("success");
    } catch (err) {
      if (controller.signal.aborted) return;
      setError(getErrorMessage(err));
      setState("error");
    }
  }, []);

  const cancel = useCallback(() => {
    controllerRef.current?.abort();
    setState("idle");
  }, []);

  const reset = useCallback(() => {
    controllerRef.current?.abort();
    setState("idle");
    setSummary("");
    setError(null);
  }, []);

  return { state, summary, error, run, cancel, reset };
}
