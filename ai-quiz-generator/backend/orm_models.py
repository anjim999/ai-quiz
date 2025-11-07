from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint
from sqlalchemy.sql import func
from database import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    date_generated = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    scraped_html = Column(Text, nullable=True)
    scraped_text = Column(Text, nullable=True)

    full_quiz_data = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint('url', name='uq_quizzes_url'),
    )
