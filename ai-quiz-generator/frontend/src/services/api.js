const BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function generateQuiz(url, forceRefresh = false, count = 10) {
  const res = await fetch(`${BASE}/generate_quiz?count=${count}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, force_refresh: forceRefresh }),
  });
  if (!res.ok) throw new Error("Failed to generate quiz");
  return res.json();
}

export async function fetchHistory() {
  const res = await fetch(`${BASE}/history`);
  if (!res.ok) throw new Error("Failed to load history");
  return res.json();
}

export async function fetchQuizById(id) {
  const res = await fetch(`${BASE}/quiz/${id}`);
  if (!res.ok) throw new Error("Quiz not found");
  return res.json();
}
