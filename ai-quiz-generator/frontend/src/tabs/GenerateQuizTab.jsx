import React, { useState } from "react";
import { generateQuiz } from "../services/api";
import QuizDisplay from "../components/QuizDisplay";

export default function GenerateQuizTab() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);
  const [takeMode, setTakeMode] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError(""); setData(null);
    if (!/^https?:\/\/.+wikipedia\.org\/wiki\/.+/.test(url)) {
      setError("Please enter a valid Wikipedia article URL.");
      return;
    }
    setLoading(true);
    try {
      const res = await generateQuiz(url);
      setData(res);
    } catch (err) {
      setError(err.message || "Failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={onSubmit} className="card">
        <label className="block text-sm font-medium mb-2">Wikipedia Article URL</label>
        <input className="input" placeholder="https://en.wikipedia.org/wiki/Alan_Turing"
               value={url} onChange={e => setUrl(e.target.value)} />
        <div className="mt-3 flex items-center gap-3">
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Generating..." : "Generate Quiz"}
          </button>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={takeMode} onChange={e => setTakeMode(e.target.checked)} />
            Take Quiz mode (hide answers)
          </label>
        </div>
        {error && <p className="mt-3 text-red-600 text-sm">{error}</p>}
      </form>

      {data && <QuizDisplay data={data} takeMode={takeMode} />}
    </div>
  );
}
