import { useEffect, useState } from "react";
import { pingServer } from "../services/api";

export type ServerStatus = "waking" | "online" | "offline";

/** Wakes the backend on page load and reports whether it is reachable. */
export function useServerStatus(): ServerStatus {
  const [status, setStatus] = useState<ServerStatus>("waking");

  useEffect(() => {
    let cancelled = false;
    pingServer().then((ok) => {
      if (!cancelled) setStatus(ok ? "online" : "offline");
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return status;
}
