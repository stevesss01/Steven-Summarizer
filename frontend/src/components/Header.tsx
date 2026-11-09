import type { ServerStatus } from "../hooks/useServerStatus";

const STATUS_LABEL: Record<ServerStatus, string> = {
  waking: "Waking server",
  online: "Server online",
  offline: "Server unreachable",
};

interface HeaderProps {
  serverStatus: ServerStatus;
}

export default function Header({ serverStatus }: HeaderProps) {
  return (
    <header className="site-header">
      <div className="container site-header__inner">
        <a className="brand" href="/" aria-label="Steven-Summarizer home">
          <span className="brand__mark" aria-hidden="true">S</span>
          <span className="brand__name">Steven-Summarizer</span>
        </a>

        <span
          className={`status-pill status-pill--${serverStatus}`}
          role="status"
        >
          <span className="status-pill__dot" aria-hidden="true" />
          {STATUS_LABEL[serverStatus]}
        </span>
      </div>
    </header>
  );
}
