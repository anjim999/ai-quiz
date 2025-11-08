import React, { useMemo, useState } from "react";

export default function QuizDisplay({ data, takeMode = false }) {
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  const score = useMemo(() => {
    if (!submitted) return 0;
    return data.quiz.reduce((acc, q, idx) => acc + (answers[idx] === q.answer ? 1 : 0), 0);
  }, [submitted, answers, data]);

  if (!data) return null;
  console.log("QuizDisplay data:", data);
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="card">
          <h2 className="text-xl font-semibold mb-2">{data.title}</h2>
          <p className="text-sm text-gray-600">{data.url}</p>
          <p className="mt-3">{data.summary}</p>
          <div className="mt-3 space-x-2">
            {data.sections?.slice(0, 6).map((s, i) => (
              <span key={i} className="badge">{s}</span>
            ))}
          </div>
        </div>
        <div className="card">
          <h3 className="font-semibold mb-2">Key Entities</h3>
          <div className="text-sm">
            <p><span className="font-medium">People:</span> {data.key_entities?.people?.join(", ") || "—"}</p>
            <p><span className="font-medium">Organizations:</span> {data.key_entities?.organizations?.join(", ") || "—"}</p>
            <p><span className="font-medium">Locations:</span> {data.key_entities?.locations?.join(", ") || "—"}</p>
          </div>
          <h3 className="font-semibold mt-4 mb-2">Related Topics</h3>
          <div className="flex flex-wrap gap-2">
            {data.related_topics?.map((t, i) => <span key={i} className="badge">{t}</span>)}
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold mb-3">Quiz</h3>
        <div className="space-y-5">
          {data.quiz?.map((q, idx) => (
            <div key={idx} className="border-b pb-4">
              <div className="flex items-center gap-2">
                <span className="badge">{q.difficulty}</span>
                <p className="font-medium">{idx + 1}. {q.question}</p>
              </div>
              <div className="mt-2 grid gap-2">
                {q.options.map((opt, i) => {
                  const id = `q${idx}-opt${i}`;
                  const checked = answers[idx] === opt;
                  return (
                    <label key={id} htmlFor={id} className="flex items-center gap-2 cursor-pointer">
                      {takeMode ? (
                        <input
                          id={id}
                          type="radio"
                          name={`q-${idx}`}
                          checked={checked}
                          onChange={() => setAnswers(a => ({ ...a, [idx]: opt }))}
                        />
                      ) : null}
                      <span className={`px-3 py-2 rounded-lg border ${!takeMode ? "bg-gray-50" : ""}`}>
                        {opt}
                      </span>
                    </label>
                  );
                })}
              </div>

              

              {takeMode && submitted && (
                <div className="mt-2 text-sm">
                  <p className={answers[idx] === q.answer ? "text-green-700" : "text-red-700"}>
                    Correct: <span className="font-semibold">{q.answer}</span>
                  </p>
                  <p className="text-gray-600">{q.explanation}</p>
                </div>
              )}
            </div>
          ))}
        </div>

        {takeMode && (
          <div className="mt-4 flex items-center gap-3">
            {!submitted ? (
              <button className="btn btn-primary" onClick={() => setSubmitted(true)}>Submit Answers</button>
            ) : (
              <>
                <span className="badge">Score: {score} / {data.quiz?.length || 0}</span>
                <button className="btn btn-ghost border" onClick={() => { setAnswers({}); setSubmitted(false); }}>
                  Reset
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
