import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Timer from "../components/Timer";
import AntiTabSwitch from "../components/AntiTabSwitch";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export default function QuizMode() {
  const nav = useNavigate();
  const active = useMemo(() => {
    const raw = localStorage.getItem("activeQuiz");
    return raw ? JSON.parse(raw) : null;
  }, []);

  const [answers, setAnswers] = useState({});
  const [strikes, setStrikes] = useState(0);
  const [submitted, setSubmitted] = useState(false);

  const startTime = useMemo(() => Date.now(), []);

  if (!active) return <div className="p-8 text-center text-xl">No active quiz. Go generate first.</div>;

  const count = active.quiz.length;
  const totalSeconds = count * 60; 

  function scoreNow() {
    let score = 0;
    active.quiz.forEach((q, i) => {
      if (answers[i] != null && q.options[answers[i]] === q.answer) score++;
    });
    return score;
  }

  async function submit(auto=false) {
    if (submitted) return;
    setSubmitted(true);

    const usedTime = Math.floor((Date.now() - startTime) / 1000);
    const score = scoreNow();

    const payload = {
      answers,
      score,
      time_taken_seconds: usedTime,
      total_time: totalSeconds,
    };

    try {
      await fetch(`${import.meta.env.VITE_API_URL}/submit_attempt/${active.id}`, {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(payload)
      });
      toast.success(`Submitted. Score ${score}/${count}`);
    } catch {
      toast.error("Save failed — but quiz ended.");
    }

    setTimeout(()=>nav("/app"), 1500);
  }

  function onStrike(n,max){
    setStrikes(n);
    if(n>=max && !submitted){
      toast.error("Tab switching detected! Auto submit");
      submit(true);
    } else {
      toast.warn(`Warning ${n}/${max}`);
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <ToastContainer />
      <div className="flex justify-between mb-4">
        <h2 className="font-semibold">{active.title}</h2>
        <Timer totalSeconds={totalSeconds} onEnd={() => submit(true)} />
      </div>

      <AntiTabSwitch maxStrikes={3} onStrike={onStrike} />

      {active.quiz.map((q,i)=>(
        <div key={i} className="p-4 border rounded-lg mb-4">
          <p className="font-medium mb-2">{i+1}. {q.question}</p>
          {q.options.map((opt,j)=>(
            <label key={j} className={`block border p-2 rounded cursor-pointer ${answers[i]===j?"border-blue-600":"border-gray-300"}`}>
              <input type="radio" name={`q${i}`} className="mr-2"
                checked={answers[i]===j}
                onChange={()=>setAnswers(a=>({...a,[i]:j}))} />
              {opt}
            </label>
          ))}
        </div>
      ))}

      <button onClick={()=>submit(false)} disabled={submitted}
        className="btn btn-primary">Submit Answers</button>
    </div>
  );
}
