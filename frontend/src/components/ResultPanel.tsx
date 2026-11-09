import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import type { ModeOption } from "../config/modes";

interface ResultPanelProps {
  summary: string;
  mode: ModeOption;
  fileName: string;
  onReset: () => void;
}

export default function ResultPanel({
  summary,
  mode,
  fileName,
  onReset,
}: ResultPanelProps) {
  const panelRef = useRef<HTMLElement>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    panelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  const copySummary = async () => {
    try {
      await navigator.clipboard.writeText(summary);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      /* Clipboard unavailable (e.g. insecure context) — ignore silently. */
    }
  };

  const downloadSummary = () => {
    const blob = new Blob([summary], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${fileName.replace(/\.pdf$/i, "")}-${mode.id}-analysis.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section ref={panelRef} className="panel result fade-in-up" aria-label="Analysis result">
      <header className="result__header">
        <div className="result__heading">
          <span className="badge badge--success">
            <span aria-hidden="true">✓</span> Analysis complete
          </span>
          <p className="result__meta">
            {mode.icon} {mode.title} · <span title={fileName}>{fileName}</span>
          </p>
        </div>

        <div className="result__actions">
          <button type="button" className="btn btn--secondary btn--sm" onClick={copySummary}>
            {copied ? "Copied" : "Copy"}
          </button>
          <button type="button" className="btn btn--secondary btn--sm" onClick={downloadSummary}>
            Download
          </button>
          <button type="button" className="btn btn--primary btn--sm" onClick={onReset}>
            New analysis
          </button>
        </div>
      </header>

      <article className="markdown">
        <ReactMarkdown>{summary}</ReactMarkdown>
      </article>
    </section>
  );
}
