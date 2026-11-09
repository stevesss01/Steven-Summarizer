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

const HIGHLIGHTS = [
  {
    title: "Structured, not generic",
    text: "Each mode uses a purpose-built prompt, so a resume gets an ATS verdict and a paper gets viva questions.",
  },
  {
    title: "Fast inference",
    text: "Llama 3.3 70B on Groq returns a full report in seconds once the server is warm.",
  },
  {
    title: "Private by design",
    text: "No sign-up and no storage. Your PDF is processed in memory and discarded.",
  },
];

export default function Home() {
  const serverStatus = useServerStatus();
  const { state, summary, error, run, cancel, reset } = useSummarize();

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
      <div className="ambient" aria-hidden="true">
        <span className="ambient__blob ambient__blob--a" />
        <span className="ambient__blob ambient__blob--b" />
        <span className="ambient__blob ambient__blob--c" />
      </div>

      <Header serverStatus={serverStatus} />

      <main className="container main">
        <section className="hero fade-in-up">
          <p className="eyebrow">AI document intelligence</p>
          <h1 className="hero__title">
            Understand any PDF <span className="gradient-text">in seconds</span>
          </h1>
          <p className="hero__lead">
            Upload a report, resume or research paper and get a clean,
            structured analysis you can act on — no sign-up required.
          </p>
        </section>

        {state === "loading" && file && (
          <LoadingState fileName={file.name} onCancel={cancel} />
        )}

        {state === "success" && file && (
          <ResultPanel
            summary={summary}
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
                {file
                  ? `Ready to run ${selectedMode.title.toLowerCase()}`
                  : "Select a PDF to get started"}
              </p>
              <button
                type="button"
                className="btn btn--primary btn--lg"
                onClick={handleAnalyse}
                disabled={!file}
              >
                Generate analysis
                <span aria-hidden="true" className="btn__arrow">→</span>
              </button>
            </div>
          </section>
        )}

        <section className="highlights" aria-label="Highlights">
          {HIGHLIGHTS.map((item, index) => (
            <article
              key={item.title}
              className="highlight fade-in-up"
              style={{ animationDelay: `${120 + index * 90}ms` }}
            >
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </article>
          ))}
        </section>
      </main>

      <Footer />
    </div>
  );
}
