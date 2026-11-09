import { useCallback, useRef, useState } from "react";
import type { AnalysisMode } from "../config/modes";
import { getErrorMessage, summarizeDocument } from "../services/api";
import type { SummaryMeta } from "../services/api";

export type RequestState = "idle" | "loading" | "success" | "error";

export function useSummarize() {
  const [state, setState] = useState<RequestState>("idle");
  const [summary, setSummary] = useState("");
  const [meta, setMeta] = useState<SummaryMeta | null>(null);
  const [error, setError] = useState<string | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const run = useCallback(async (file: File, mode: AnalysisMode, context = "") => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    setState("loading");
    setError(null);
    setSummary("");
    setMeta(null);

    try {
      const result = await summarizeDocument(file, mode, context, controller.signal);
      setSummary(result.summary);
      setMeta(result.meta ?? null);
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
    setMeta(null);
    setError(null);
  }, []);

  return { state, summary, meta, error, run, cancel, reset };
}
