import { useRef, useState } from "react";
import type { DragEvent, KeyboardEvent } from "react";
import { MAX_UPLOAD_MB } from "../config/modes";

interface UploadZoneProps {
  file: File | null;
  disabled?: boolean;
  onFileSelect: (file: File | null) => void;
  onError: (message: string) => void;
}

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function UploadZone({
  file,
  disabled = false,
  onFileSelect,
  onError,
}: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const acceptFile = (candidate: File | undefined) => {
    if (!candidate) return;
    const isPdf =
      candidate.type === "application/pdf" ||
      candidate.name.toLowerCase().endsWith(".pdf");

    if (!isPdf) {
      onError("Please choose a PDF file.");
      return;
    }
    if (candidate.size > MAX_UPLOAD_MB * 1024 * 1024) {
      onError(`File is larger than ${MAX_UPLOAD_MB} MB.`);
      return;
    }
    onFileSelect(candidate);
  };

  const openPicker = () => {
    if (!disabled) inputRef.current?.click();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (!disabled) acceptFile(e.dataTransfer.files[0]);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      openPicker();
    }
  };

  const classes = [
    "dropzone",
    isDragging && "dropzone--dragging",
    file && "dropzone--filled",
    disabled && "dropzone--disabled",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      className={classes}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label="Upload a PDF document"
      aria-disabled={disabled}
      onClick={openPicker}
      onKeyDown={handleKeyDown}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf,.pdf"
        hidden
        onChange={(e) => {
          acceptFile(e.target.files?.[0]);
          e.target.value = "";
        }}
      />

      {file ? (
        <div className="file-chip" onClick={(e) => e.stopPropagation()}>
          <span className="file-chip__icon" aria-hidden="true">PDF</span>
          <span className="file-chip__meta">
            <span className="file-chip__name" title={file.name}>
              {file.name}
            </span>
            <span className="file-chip__size">{formatSize(file.size)}</span>
          </span>
          {!disabled && (
            <button
              type="button"
              className="file-chip__remove"
              aria-label="Remove file"
              onClick={() => onFileSelect(null)}
            >
              ×
            </button>
          )}
        </div>
      ) : (
        <div className="dropzone__prompt">
          <span className="dropzone__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="28" height="28" fill="none"
              stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"
              strokeLinejoin="round">
              <path d="M12 16V4" />
              <path d="m7 9 5-5 5 5" />
              <path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
            </svg>
          </span>
          <p className="dropzone__title">
            Drop your PDF here or <span className="link-text">browse</span>
          </p>
          <p className="dropzone__hint">Text-based PDFs up to {MAX_UPLOAD_MB} MB</p>
        </div>
      )}
    </div>
  );
}
