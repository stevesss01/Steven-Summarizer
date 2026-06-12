import React from "react";

interface UploadZoneProps {
  file: File | null;
  onFileSelect: (
    file: File | null
  ) => void;
}

export default function UploadZone({
  file,
  onFileSelect
}: UploadZoneProps) {

  const handleDrop = (
    e: React.DragEvent
  ) => {

    e.preventDefault();

    const droppedFile =
      e.dataTransfer.files[0];

    if (
      droppedFile &&
      droppedFile.type ===
        "application/pdf"
    ) {
      onFileSelect(
        droppedFile
      );
    }
  };

  return (
    <div
      onDragOver={(e) =>
        e.preventDefault()
      }
      onDrop={handleDrop}
      style={{
        border:
          "2px dashed #475569",
        borderRadius:
          "16px",
        padding: "50px",
        textAlign:
          "center",
        background:
          "#0f172a",
        cursor: "pointer"
      }}
    >
      <input
        type="file"
        accept=".pdf"
        style={{
          display: "none"
        }}
        id="pdf-upload"
        onChange={(e) =>
          onFileSelect(
            e.target.files?.[0]
              || null
          )
        }
      />

      <label
        htmlFor="pdf-upload"
        style={{
          cursor: "pointer"
        }}
      >
        <h2>
          📄 Upload PDF
        </h2>

        <p>
          Drag & Drop or
          Click to Browse
        </p>

        {file && (
          <p
            style={{
              marginTop:
                "15px",
              color:
                "#38bdf8"
            }}
          >
            {file.name}
          </p>
        )}
      </label>
    </div>
  );
}