import { useEffect, useState } from "react";

export default function Timer({ totalSeconds, onEnd }) {
  const [sec, setSec] = useState(totalSeconds);
  useEffect(() => {
    if (sec <= 0) { onEnd?.(); return; }
    const t = setTimeout(() => setSec(s => s - 1), 1000);
    return () => clearTimeout(t);
  }, [sec, onEnd]);
  const m = Math.floor(sec/60).toString().padStart(2,"0");
  const s = (sec%60).toString().padStart(2,"0");
  return <div className="font-mono text-lg">{m}:{s}</div>;
}
