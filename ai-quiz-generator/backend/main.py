import json
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import Base, engine, SessionLocal
from orm_models import Quiz
from schemas import GenerateRequest, HistoryItem, HistoryResponse
from scraper import scrape_wikipedia
from llm_quiz_generator import generate_quiz_payload
from utils import is_wikipedia_url

load_dotenv()

app = FastAPI(title="AI Wiki Quiz Generator", version="1.0.0")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
def generate_quiz(req: GenerateRequest, db: Session = Depends(get_db)):
    url = str(req.url)

    if not is_wikipedia_url(url):
        raise HTTPException(status_code=400, detail="Only Wikipedia article URLs are accepted (HTML scraping only).")

    # Cache: return existing if present and not force_refresh
    use_cache = os.getenv("ENABLE_URL_CACHE", "true").lower() == "true"
    if use_cache and not req.force_refresh:
        existing = db.query(Quiz).filter(Quiz.url == url).one_or_none()
        if existing:
            data = json.loads(existing.full_quiz_data)
            data["id"] = existing.id
            return data

    # Scrape
    try:
        title, cleaned_text, sections, raw_html = scrape_wikipedia(url)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to scrape URL: {e}")

    if not cleaned_text or len(cleaned_text) < 200:
        raise HTTPException(status_code=422, detail="Article content seems too short or could not be parsed.")

    # Generate with LLM (or fallback)
    try:
        payload = generate_quiz_payload(url=url, title=title, article_text=cleaned_text, sections=sections)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation error: {e}")

    payload["sections"] = payload.get("sections") or sections
    # Persist
    record = db.query(Quiz).filter(Quiz.url == url).one_or_none()
    if record is None:
        record = Quiz(
            url=url,
            title=title,
            scraped_html=raw_html,
            scraped_text=cleaned_text,
            full_quiz_data=json.dumps(payload, ensure_ascii=False),
        )
        db.add(record)
        try:
            db.commit()
            db.refresh(record)
        except IntegrityError:
            db.rollback()
            record = db.query(Quiz).filter(Quiz.url == url).one()
    else:
        record.title = title
        record.scraped_html = raw_html
        record.scraped_text = cleaned_text
        record.full_quiz_data = json.dumps(payload, ensure_ascii=False)
        db.commit()
        db.refresh(record)

    payload["id"] = record.id
    return payload

@app.get("/history", response_model=HistoryResponse)
def history(db: Session = Depends(get_db)):
    rows = db.query(Quiz).order_by(Quiz.date_generated.desc()).all()
    items = [
        HistoryItem(
            id=r.id,
            url=r.url,
            title=r.title,
            date_generated=r.date_generated.isoformat() if r.date_generated else ""
        )
        for r in rows
    ]
    return HistoryResponse(items=items)

@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    r = db.query(Quiz).filter(Quiz.id == quiz_id).one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Quiz not found")
    data = json.loads(r.full_quiz_data)
    data["id"] = r.id
    return data
