import { useState } from "react";
import { generateQuiz } from "../services/api";
import QuizDisplay from "../components/QuizDisplay";
import { useNavigate } from "react-router-dom";

const COUNTS = [10, 20, 30, 40, 50];

export default function GenerateQuizTab() {
  const [url, setUrl] = useState("");
  const [count, setCount] = useState(10);
  const [hideAnswers, setHideAnswers] = useState(false);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleGenerate() {
    if (!url.trim()) return;
    setLoading(true);
    setData(null);
    try {
      const res = await generateQuiz(url, false, count);
      setData(res);
      localStorage.setItem("activeQuiz", JSON.stringify(res));
    } catch {
      alert("Quiz generation failed");
    }
    setLoading(false);
  }

  return (
    <div className="space-y-6">
      <label className="font-medium text-gray-700">Wikipedia Article URL</label>
      <input
        className="input input-bordered w-full"
        placeholder="https://en.wikipedia.org/wiki/Alan_Turing"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />

      <div className="flex items-center gap-4">
        <label>Questions:</label>
        <select
          className="select select-bordered"
          value={count}
          onChange={(e) => setCount(Number(e.target.value))}
        >
          {COUNTS.map((n) => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>

        

        <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
          {loading ? "Generating..." : "Generate Quiz"}
        </button>

        {data && (
          <button className="btn btn-success text-white" onClick={() => navigate("/exam")}>
            Start Quiz
          </button>
        )}
      </div>

      {data && <QuizDisplay data={data} hideAnswers={hideAnswers} />}
    </div>
  );
}
