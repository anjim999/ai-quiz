import { useEffect, useRef } from "react";

export default function AntiTabSwitch({ onStrike, maxStrikes=3 }) {
  const strikes = useRef(0);
  useEffect(() => {
    const handle = () => {
      strikes.current += 1;
      onStrike?.(strikes.current, maxStrikes);
    };
    const blur = () => handle();
    const vis = () => { if (document.hidden) handle(); };
    window.addEventListener("blur", blur);
    document.addEventListener("visibilitychange", vis);
    return () => {
      window.removeEventListener("blur", blur);
      document.removeEventListener("visibilitychange", vis);
    };
  }, [onStrike, maxStrikes]);
  return null;
}
