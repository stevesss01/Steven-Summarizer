import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import type { ModeOption } from "../config/modes";
import type { SummaryMeta } from "../services/api";
import { downloadReportPdf } from "../services/api";

interface ResultPanelProps {
  summary: string;
  meta: SummaryMeta | null;
  mode: ModeOption;
  fileName: string;
  onReset: () => void;
}

export default function ResultPanel({
  summary,
  meta,
  mode,
  fileName,
  onReset,
}: ResultPanelProps) {
  const panelRef = useRef<HTMLElement>(null);
  const [copied, setCopied] = useState(false);
  const [pdfState, setPdfState] = useState<"idle" | "working" | "error">("idle");

  useEffect(() => {
    panelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  const copySummary = async () => {
    try {
      await navigator.clipboard.writeText(summary);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      // Clipboard API is unavailable in insecure contexts; nothing to do.
    }
  };

  const downloadPdf = async () => {
    setPdfState("working");
    try {
      await downloadReportPdf(summary, mode.title, fileName);
      setPdfState("idle");
    } catch {
      setPdfState("error");
    }
  };

  return (
    <section
      ref={panelRef}
      className="panel result fade-in-up"
      aria-label="Analysis result"
    >
      <header className="result__header">
        <div className="result__heading">
          <span className="badge badge--success">
            <span className="badge__dot" aria-hidden="true" /> Analysis complete
          </span>
          <p className="result__meta">
            {mode.title} · <span title={fileName}>{fileName}</span>
          </p>
          {meta && (
            <p className="result__stats">
              <span>
                {meta.pages} {meta.pages === 1 ? "page" : "pages"}
              </span>
              {meta.sections > 1 && (
                <span>Analysed in {meta.sections} parallel sections</span>
              )}
              <span>{meta.seconds}s</span>
            </p>
          )}
        </div>

        <div className="result__actions">
          <button
            type="button"
            className="btn btn--secondary btn--sm"
            onClick={copySummary}
          >
            {copied ? "Copied" : "Copy"}
          </button>
          <button
            type="button"
            className="btn btn--secondary btn--sm"
            onClick={downloadPdf}
            disabled={pdfState === "working"}
            aria-busy={pdfState === "working"}
          >
            {pdfState === "working" ? (
              <>
                <span className="btn-spinner" aria-hidden="true" /> Preparing PDF
              </>
            ) : (
              "Download PDF"
            )}
          </button>
          <button type="button" className="btn btn--primary btn--sm" onClick={onReset}>
            New analysis
          </button>
        </div>
      </header>

      {pdfState === "error" && (
        <p className="result__note result__note--error" role="alert">
          The PDF could not be generated. Please try again, or use Copy.
        </p>
      )}

      {meta?.truncated && (
        <p className="result__note">
          This document is very long, so only the first {meta.pages_analysed} pages (or
          the first part of the text) were analysed.
        </p>
      )}

      <article className="markdown">
        <ReactMarkdown>{summary}</ReactMarkdown>
      </article>
    </section>
  );
}
