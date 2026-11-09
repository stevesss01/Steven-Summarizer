import type { AnalysisMode } from "../config/modes";
import { MODES } from "../config/modes";
import ModeIcon from "./ModeIcon";

interface ModeSelectorProps {
  value: AnalysisMode;
  disabled?: boolean;
  onChange: (mode: AnalysisMode) => void;
}

export default function ModeSelector({
  value,
  disabled = false,
  onChange,
}: ModeSelectorProps) {
  return (
    <div className="mode-grid" role="radiogroup" aria-label="Analysis type">
      {MODES.map((mode) => {
        const selected = mode.id === value;
        return (
          <button
            key={mode.id}
            type="button"
            role="radio"
            aria-checked={selected}
            disabled={disabled}
            className={`mode-card${selected ? " mode-card--selected" : ""}`}
            onClick={() => onChange(mode.id)}
          >
            <span className="mode-card__icon" aria-hidden="true">
              <ModeIcon mode={mode.id} />
            </span>
            <span className="mode-card__text">
              <span className="mode-card__title">{mode.title}</span>
              <span className="mode-card__desc">{mode.description}</span>
            </span>
            <span className="mode-card__check" aria-hidden="true" />
          </button>
        );
      })}
    </div>
  );
}
