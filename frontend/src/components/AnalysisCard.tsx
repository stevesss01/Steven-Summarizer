interface Props {
  title: string;
  icon: string;
  selected: boolean;
  onClick: () => void;
}

export default function AnalysisCard({
  title,
  icon,
  selected,
  onClick
}: Props) {

  return (
    <div
      onClick={onClick}
      style={{
        background:
          selected
            ? "#2563eb"
            : "#1e293b",
        border:
          selected
            ? "2px solid #38bdf8"
            : "1px solid #334155",
        borderRadius:
          "16px",
        padding: "25px",
        cursor: "pointer",
        textAlign:
          "center",
        transition:
          "0.3s"
      }}
    >
      <h2>{icon}</h2>

      <h3>{title}</h3>
    </div>
  );
}