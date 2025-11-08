# pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

def build_exam_pdf(filename: str, org_title: str, user: str, quiz_title: str, quiz: dict, duration_str: str):
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm
    )
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"<b>{org_title}</b>", styles["Title"]))
    story.append(Paragraph(quiz_title, styles["h2"]))
    story.append(Paragraph(f"Candidate: <b>{user or 'Anonymous'}</b>", styles["Normal"]))
    story.append(Paragraph(f"Duration: <b>{duration_str}</b> (1 min/question)", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Questions (choices only)
    letters = "ABCD"
    for i, q in enumerate(quiz.get("quiz", []), start=1):
        story.append(Paragraph(f"<b>Q{i}.</b> {q['question']}", styles["BodyText"]))
        for j, opt in enumerate(q["options"]):
            story.append(Paragraph(f"{letters[j]}) {opt}", styles["BodyText"]))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 16))
    story.append(Paragraph("<b>Answer Key</b>", styles["h2"]))
    for i, q in enumerate(quiz.get("quiz", []), start=1):
        ans = q["answer"]
        j = next((k for k, o in enumerate(q["options"]) if o == ans), None)
        letter = letters[j] if j is not None else "?"
        story.append(Paragraph(f"Q{i}: <b>{letter}</b>", styles["BodyText"]))

    doc.build(story)
    return filename
