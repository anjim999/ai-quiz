# main.py
import json, os, io
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime, timezone
import tempfile


from database import Base, engine, SessionLocal
from orm_models import Quiz, Attempt
from schemas import GenerateRequest, HistoryItem, HistoryResponse
from scraper import scrape_wikipedia
from llm_quiz_generator import generate_quiz_payload
from utils import is_wikipedia_url
from pdf_generator import build_exam_pdf

load_dotenv()

app = FastAPI(title="AI Wiki Quiz Generator", version="1.1.0")

# Open CORS (frontend localhost/Vercel, etc.)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://ai-quiz-generator-jade.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ✅ use allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate_quiz")
def generate_quiz(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    count: int = Query(10, ge=5, le=50)   # ✅ reads ?count= from frontend URL
):
    url = str(req.url)

    print("Generating quiz for URL:", url, "with count:", count)

    if not is_wikipedia_url(url):
        raise HTTPException(status_code=400, detail="Only Wikipedia article URLs are accepted.")

    use_cache = os.getenv("ENABLE_URL_CACHE", "true").lower() == "true"
    existing = db.query(Quiz).filter(Quiz.url == url).one_or_none()

    # ✅ Return cached quiz if exists & not forcing refresh
    if use_cache and existing and not req.force_refresh:
        stored = json.loads(existing.full_quiz_data)
        stored_count = len(stored.get("quiz", []))

        # ✅ Enough questions stored → slice and return
        if stored_count >= count:
            stored["quiz"] = stored["quiz"][:count]
            stored["id"] = existing.id
            return stored
        # ❌ Not enough → regenerate

    # ✅ Fresh scrape and LLM call
    title, cleaned_text, sections, raw_html = scrape_wikipedia(url)
    if not cleaned_text or len(cleaned_text) < 200:
        raise HTTPException(status_code=422, detail="Article content too short or could not be parsed.")

    payload = generate_quiz_payload(
    url=url,
    title=title,
    article_text=cleaned_text,
    sections=sections,
    count=count   # ✅ pass count from frontend
)


    # ✅ Trim to requested question count
    payload["quiz"] = (payload.get("quiz") or [])[:count]
    payload["sections"] = payload.get("sections") or sections

    # ✅ Insert or update DB
    if not existing:
        record = Quiz(
            url=url, title=title,
            scraped_html=raw_html, scraped_text=cleaned_text,
            full_quiz_data=json.dumps(payload, ensure_ascii=False)
        )
        db.add(record)
        db.commit()
        db.refresh(record)
    else:
        existing.title = title
        existing.scraped_html = raw_html
        existing.scraped_text = cleaned_text
        existing.full_quiz_data = json.dumps(payload, ensure_ascii=False)
        db.commit()
        db.refresh(existing)
        record = existing

    payload["id"] = record.id
    return payload

@app.get("/history", response_model=HistoryResponse)
def history(db: Session = Depends(get_db)):
    rows = db.query(Quiz).order_by(Quiz.date_generated.desc()).all()
    return HistoryResponse(items=[
        HistoryItem(
            id=r.id, url=r.url, title=r.title,
            date_generated=r.date_generated.isoformat() if r.date_generated else ""
        ) for r in rows
    ])

@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    r = db.query(Quiz).filter(Quiz.id == quiz_id).one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Quiz not found")
    data = json.loads(r.full_quiz_data); data["id"] = r.id
    return data

@app.post("/submit_attempt/{quiz_id}")
def submit_attempt(quiz_id: int, payload: dict, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    answers = payload.get("answers", {})
    score = int(payload.get("score", 0))

    # ✅ use time_taken_seconds coming from frontend
    time_taken = int(payload.get("time_taken_seconds", 0))

    # ✅ also capture total allotted time if sent
    total_time = int(payload.get("total_time", 0))

    attempt = Attempt(
        quiz_id=quiz_id,
        time_taken_seconds=time_taken,  # ✅ store actual time taken
        total_time=total_time,
        score=score,
        answers_json=json.dumps(answers),
        # set submission timestamp so submitted_at is not NULL
        submitted_at=datetime.now(timezone.utc),
    )

    print(attempt)

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {"saved": True, "attempt_id": attempt.id}

@app.post("/export_pdf/{quiz_id}")
def export_pdf(quiz_id: int, payload: dict, db: Session = Depends(get_db)):
    r = db.query(Quiz).filter(Quiz.id == quiz_id).one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Quiz not found")
    q = json.loads(r.full_quiz_data); q["id"] = r.id

    count = int(payload.get("count", len(q["quiz"])))
    q["quiz"] = q["quiz"][:count]
    user = payload.get("user", "Anonymous")
    duration_str = payload.get("duration_str", "—")

    filename = f"quiz_{quiz_id}.pdf"

    # ✅ Cross-platform temp directory
    import tempfile, os
    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, filename)

    # ✅ Build PDF
    build_exam_pdf(tmp_path, "DeepKlarity AI Exam", user, q.get("title","Quiz"), q, duration_str)

    with open(tmp_path, "rb") as f:
        pdf_bytes = f.read()

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
