import { useEffect, useState } from "react";

const STEPS = [
  { label: "Uploading document", after: 0 },
  { label: "Reading pages", after: 1800 },
  { label: "Analysing content", after: 4500 },
  { label: "Structuring your report", after: 9000 },
];

/** Shown after this long, explaining the free-tier server cold start. */
const SLOW_HINT_AFTER = 14000;

interface LoadingStateProps {
  fileName: string;
  onCancel: () => void;
}

export default function LoadingState({ fileName, onCancel }: LoadingStateProps) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const start = Date.now();
    const id = window.setInterval(() => setElapsed(Date.now() - start), 500);
    return () => window.clearInterval(id);
  }, []);

  const activeIndex = STEPS.reduce(
    (current, step, index) => (elapsed >= step.after ? index : current),
    0,
  );

  return (
    <section className="panel loading fade-in" aria-live="polite" aria-busy="true">
      <div className="loading__visual" aria-hidden="true">
        <span className="breath-ring breath-ring--outer" />
        <span className="breath-ring breath-ring--mid" />
        <span className="breath-ring breath-ring--inner" />
        <span className="loading__doc">
          <span className="loading__doc-line" />
          <span className="loading__doc-line" />
          <span className="loading__doc-line loading__doc-line--short" />
          <span className="loading__scan" />
        </span>
      </div>

      <div className="loading__body">
        <p className="eyebrow">Analysing</p>
        <h2 className="loading__title" title={fileName}>
          {fileName}
        </h2>

        <ol className="steps">
          {STEPS.map((step, index) => {
            const status =
              index < activeIndex ? "done" : index === activeIndex ? "active" : "pending";
            return (
              <li key={step.label} className={`step step--${status}`}>
                <span className="step__marker" aria-hidden="true" />
                <span className="step__label">{step.label}</span>
              </li>
            );
          })}
        </ol>

        <p className={`loading__hint${elapsed > SLOW_HINT_AFTER ? " is-visible" : ""}`}>
          Still working. Long documents are split into sections and analysed in parallel,
          and the free server may also need a moment to wake up.
        </p>

        <button type="button" className="btn btn--ghost btn--sm" onClick={onCancel}>
          Cancel
        </button>
      </div>

      <div className="skeleton" aria-hidden="true">
        <span className="skeleton__line skeleton__line--title" />
        <span className="skeleton__line" />
        <span className="skeleton__line skeleton__line--90" />
        <span className="skeleton__line skeleton__line--75" />
        <span className="skeleton__line skeleton__line--subtitle" />
        <span className="skeleton__line skeleton__line--85" />
        <span className="skeleton__line skeleton__line--60" />
      </div>
    </section>
  );
}
