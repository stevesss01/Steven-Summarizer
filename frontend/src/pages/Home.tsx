import { useState } from "react";
import ErrorBanner from "../components/ErrorBanner";
import Footer from "../components/Footer";
import Header from "../components/Header";
import LoadingState from "../components/LoadingState";
import ModeSelector from "../components/ModeSelector";
import ResultPanel from "../components/ResultPanel";
import UploadZone from "../components/UploadZone";
import type { AnalysisMode } from "../config/modes";
import { MODES } from "../config/modes";
import { useServerStatus } from "../hooks/useServerStatus";
import { useSummarize } from "../hooks/useSummarize";

export default function Home() {
  const serverStatus = useServerStatus();
  const { state, summary, meta, error, run, cancel, reset } = useSummarize();

  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<AnalysisMode>("general");
  const [localError, setLocalError] = useState<string | null>(null);

  const selectedMode = MODES.find((m) => m.id === mode) ?? MODES[0];
  const visibleError = localError ?? error;

  const handleAnalyse = () => {
    if (!file) {
      setLocalError("Please upload a PDF first.");
      return;
    }
    setLocalError(null);
    run(file, mode);
  };

  const handleReset = () => {
    reset();
    setFile(null);
    setLocalError(null);
  };

  return (
    <div className="page">
      <Header serverStatus={serverStatus} />

      <main className="container main">
        <section className="intro">
          <h1 className="intro__title">Document analysis</h1>
          <p className="intro__lead">
            Upload a PDF and choose how it should be read: an executive brief, a resume
            review or a research paper breakdown.
          </p>
        </section>

        {state === "loading" && file && (
          <LoadingState fileName={file.name} onCancel={cancel} />
        )}

        {state === "success" && file && (
          <ResultPanel
            summary={summary}
            meta={meta}
            mode={selectedMode}
            fileName={file.name}
            onReset={handleReset}
          />
        )}

        {(state === "idle" || state === "error") && (
          <section className="panel workspace fade-in-up" aria-label="New analysis">
            <div className="workspace__step">
              <h2 className="step-heading">
                <span className="step-heading__num">1</span> Upload your document
              </h2>
              <UploadZone
                file={file}
                onFileSelect={(f) => {
                  setFile(f);
                  setLocalError(null);
                }}
                onError={setLocalError}
              />
            </div>

            <div className="workspace__step">
              <h2 className="step-heading">
                <span className="step-heading__num">2</span> Choose an analysis
              </h2>
              <ModeSelector value={mode} onChange={setMode} />
            </div>

            {visibleError && (
              <ErrorBanner
                message={visibleError}
                onDismiss={() => {
                  setLocalError(null);
                  if (state === "error") reset();
                }}
              />
            )}

            <div className="workspace__footer">
              <p className="workspace__note">
                Files are processed in memory and never stored.
              </p>
              <button
                type="button"
                className="btn btn--primary btn--lg"
                onClick={handleAnalyse}
                disabled={!file}
              >
                Analyse document
              </button>
            </div>
          </section>
        )}
      </main>

      <Footer />
    </div>
  );
}
