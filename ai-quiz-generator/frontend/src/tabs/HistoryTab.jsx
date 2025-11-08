import React, { useEffect, useState } from "react";
import { fetchHistory, fetchQuizById } from "../services/api";
import HistoryTable from "../components/HistoryTable";
import Modal from "../components/Modal";
import QuizDisplay from "../components/QuizDisplay";
import PDFExportButton from "../components/PDFExportButton";

export default function HistoryTab() {
  const [rows, setRows] = useState([]);
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      const res = await fetchHistory();
      setRows(res.items || []);
    } catch (e) {
      setError("Failed to load history");
    }
  }

  useEffect(() => { load(); }, []);

  async function handleDetails(id) {
    try {
      const data = await fetchQuizById(id);
      setSelected(data);
      setOpen(true);
    } catch {
      setSelected(null);
      setOpen(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Past Quizzes</h3>
        <button className="btn btn-ghost border" onClick={load}>Refresh</button>
      </div>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <HistoryTable items={rows} onDetails={handleDetails} />

      <Modal open={open} onClose={() => setOpen(false)} title={selected?.title || "Details"}>
        {selected ? (
          <>
            <div className="mb-4">
              <PDFExportButton
                quizId={selected.id}
                count={selected.quiz?.length || 10}
                durationStr={`${Math.ceil((selected.quiz?.length || 10))} min`}
              />
            </div>
            <QuizDisplay data={selected} />
          </>
        ) : <p>Loading…</p>}
      </Modal>
    </div>
  );
}
