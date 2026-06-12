
import { useState } from "react";
import { api } from "../services/api";
import ReactMarkdown from "react-markdown";
import UploadZone from "../components/UploadZone";
import AnalysisCard from "../components/AnalysisCard";

export default function Home() {

  const [file, setFile] =
    useState<File | null>(null);

  const [summary, setSummary] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [mode, setMode] =
    useState("general");

  const resetAnalysis = () => {

    setFile(null);

    setSummary("");

    setMode("general");

  };

  const generateSummary =
    async () => {

      if (!file) {

        alert(
          "Please upload a PDF"
        );

        return;
      }

      setLoading(true);

      const formData =
        new FormData();

      formData.append(
        "file",
        file
      );

      formData.append(
        "mode",
        mode
      );

      try {

        const res =
          await api.post(
            "/summarize",
            formData,
            {
              headers: {
                "Content-Type":
                  "multipart/form-data"
              }
            }
          );

        setSummary(
          res.data.summary
        );

      } catch (err) {

        console.error(err);

        alert(
          "Failed to summarize"
        );

      } finally {

        setLoading(false);

      }
    };

  const downloadSummary =
    () => {

      const blob =
        new Blob(
          [summary],
          {
            type:
              "text/plain"
          }
        );

      const url =
        URL.createObjectURL(
          blob
        );

      const a =
        document.createElement(
          "a"
        );

      a.href = url;

      a.download =
        "Steven-Analysis.txt";

      a.click();

      URL.revokeObjectURL(
        url
      );
    };

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg,#020617,#0f172a)",
        color: "white",
        display: "flex",
        justifyContent:
          "center",
        alignItems: "center",
        padding: "40px"
      }}
    >
      <div
        style={{
          maxWidth: "1100px",
          width: "100%",
          background:
            "#1e293b",
          padding: "40px",
          borderRadius: "20px",
          boxShadow:
            "0 0 30px rgba(0,0,0,0.4)"
        }}
      >
        <h1
          style={{
            textAlign: "center",
            fontSize: "48px",
            marginBottom: "10px"
          }}
        >
          Steven-Summarizer
        </h1>

        <p
          style={{
            textAlign: "center",
            color: "#94a3b8",
            fontSize: "18px"
          }}
        >
          AI-Powered Document Intelligence
        </p>

        <div
          style={{
            textAlign: "center",
            marginTop: "10px",
            color: "#64748b",
            marginBottom: "30px"
          }}
        >
          Fast • Accurate • Secure
        </div>

        <UploadZone
          file={file}
          onFileSelect={setFile}
        />

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(3,1fr)",
            gap: "20px",
            marginTop: "30px"
          }}
        >
          <AnalysisCard
            title="General Summary"
            icon="📄"
            selected={
              mode === "general"
            }
            onClick={() =>
              setMode(
                "general"
              )
            }
          />

          <AnalysisCard
            title="Resume Review"
            icon="📋"
            selected={
              mode === "resume"
            }
            onClick={() =>
              setMode(
                "resume"
              )
            }
          />

          <AnalysisCard
            title="Research Paper"
            icon="🔬"
            selected={
              mode === "research"
            }
            onClick={() =>
              setMode(
                "research"
              )
            }
          />
        </div>

        <div
          style={{
            textAlign: "center"
          }}
        >
          <button
            onClick={
              generateSummary
            }
            disabled={
              loading
            }
            style={{
              marginTop: "30px",
              padding:
                "14px 35px",
              border: "none",
              borderRadius:
                "12px",
              background:
                "#2563eb",
              color: "white",
              cursor:
                "pointer",
              fontSize:
                "16px",
              fontWeight:
                "bold"
            }}
          >
            {loading
              ? "⏳ Analyzing Document..."
              : "Generate Analysis"}
          </button>
        </div>

        {summary && (
          <>
            <div
              style={{
                background:
                  "#14532d",
                padding: "12px",
                borderRadius:
                  "10px",
                marginTop: "25px",
                textAlign:
                  "center"
              }}
            >
              ✅ Analysis Complete
            </div>

            <div
              style={{
                marginTop: "30px",
                textAlign:
                  "center"
              }}
            >
              <button
                onClick={
                  downloadSummary
                }
                style={{
                  padding:
                    "12px 24px",
                  border: "none",
                  borderRadius:
                    "10px",
                  background:
                    "#22c55e",
                  color: "white",
                  cursor:
                    "pointer"
                }}
              >
                Download Analysis
              </button>

              <button
                onClick={
                  resetAnalysis
                }
                style={{
                  marginLeft:
                    "15px",
                  padding:
                    "12px 24px",
                  border: "none",
                  borderRadius:
                    "10px",
                  background:
                    "#475569",
                  color: "white",
                  cursor:
                    "pointer"
                }}
              >
                New Analysis
              </button>
            </div>

            <div
              style={{
                marginTop: "30px",
                background:
                  "#0f172a",
                padding: "30px",
                borderRadius:
                  "16px",
                border:
                  "1px solid #334155",
                lineHeight:
                  "1.8"
              }}
            >
              <h2>
                Analysis Result
              </h2>

              <ReactMarkdown>
                {summary}
              </ReactMarkdown>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

