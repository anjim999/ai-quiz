export default function PDFExportButton({ quizId, count, durationStr }) {
  const handle = async () => {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/export_pdf/${quizId}`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ user: "Candidate", count, duration_str: durationStr })
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `quiz_${quizId}.pdf`; a.click();
    URL.revokeObjectURL(url);
  };
  return <button className="btn btn-outline" onClick={handle}>Export PDF</button>;
}
