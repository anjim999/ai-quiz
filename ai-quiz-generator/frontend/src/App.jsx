import React, { useState } from "react";
import GenerateQuizTab from "./tabs/GenerateQuizTab";
import HistoryTab from "./tabs/HistoryTab";

export default function App() {
  const [tab, setTab] = useState("generate");

  return (
    <div className="max-w-6xl mx-auto p-5">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">AI Wiki Quiz Generator</h1>
        <p className="text-gray-600">Enter a Wikipedia URL, generate a quiz, and view your history.</p>
      </header>

      <div className="flex gap-2 mb-4">
        <button className={`btn ${tab === "generate" ? "btn-primary" : "btn-ghost border"}`} onClick={() => setTab("generate")}>Generate Quiz</button>
        <button className={`btn ${tab === "history" ? "btn-primary" : "btn-ghost border"}`} onClick={() => setTab("history")}>Past Quizzes</button>
      </div>

      {tab === "generate" ? <GenerateQuizTab /> : <HistoryTab />}
      <footer className="mt-10 text-center text-xs text-gray-500">DeepKlarity Assignment • FastAPI + React</footer>
    </div>
  );
}
