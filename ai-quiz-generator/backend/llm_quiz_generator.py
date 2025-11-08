# llm_quiz_generator.py
import os
from typing import Dict, Any
import os
from typing import Dict, Any
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser

from schemas import QuizOutput

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def _fallback_quiz(url: str, title: str, text: str, sections: list[str]) -> Dict[str, Any]:
    base_options = ["Yes", "No", "Not stated", "Irrelevant"]
    quiz = []
    for _ in range(5):
        quiz.append({
            "question": f"Is this article about '{title}'?",
            "options": base_options,
            "answer": "Yes",
            "difficulty": "easy",
            "explanation": "Fallback used because GEMINI_API_KEY is not configured."
        })
    return {
        "url": url,
        "title": title,
        "summary": f"Placeholder summary for {title}. Configure GEMINI_API_KEY for real AI output.",
        "key_entities": {"people": [], "organizations": [], "locations": []},
        "sections": sections[:8],
        "quiz": quiz,
        "related_topics": ["Wikipedia", "Encyclopedia", "Article"]
    }


def build_chain():
    parser = PydanticOutputParser(pydantic_object=QuizOutput)
    prompt = PromptTemplate(
        template=(
            "You will generate a quiz and metadata in strict JSON.\n"
            "URL: {url}\nTITLE: {title}\n\n"
            "ARTICLE_TEXT:\n{article_text}\n\n"
            "Generate exactly {question_count} high-quality multiple-choice questions (4 options each).\n"
            "Follow this schema exactly:\n{format_instructions}\n"
        ),
        input_variables=["url", "title", "article_text", "question_count"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", api_key=GEMINI_API_KEY, temperature=0.2)
    return prompt | llm | parser


_chain = None


def ensure_chain():
    global _chain
    if _chain is None:
        _chain = build_chain()
    return _chain


def generate_quiz_payload(
    url: str,
    title: str,
    article_text: str,
    sections: list[str],
    count: int = 10,  # requested number of questions
) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        data = _fallback_quiz(url, title, article_text, sections)
        data["quiz"] = data.get("quiz", [])[:count]
        return data

    chain = ensure_chain()

    # first attempt: ask for the full set
    result: QuizOutput = chain.invoke({
        "url": url,
        "title": title,
        "article_text": article_text,
        "question_count": str(count),
    })

    quiz = [q.model_dump() for q in result.quiz]
    quiz = quiz[:count]

    # If model returned fewer than requested, attempt to generate the remainder up to 3 attempts
    attempts = 0
    max_attempts = 3
    while len(quiz) < count and attempts < max_attempts:
        attempts += 1
        remaining = count - len(quiz)

        # Add previously generated questions as context to avoid duplicates
        prev_q_text = "\n".join([f"- {i+1}. {q['question']}" for i, q in enumerate(quiz)])
        extra_article = article_text + "\n\nPreviously generated questions:\n" + (prev_q_text or "None")

        try:
            more_result: QuizOutput = chain.invoke({
                "url": url,
                "title": title,
                "article_text": extra_article,
                "question_count": str(remaining),
            })
        except Exception:
            break

        more_quiz = [q.model_dump() for q in more_result.quiz]

        # append new non-duplicate questions
        existing_questions = {q["question"] for q in quiz}
        for mq in more_quiz:
            if mq.get("question") and mq["question"] not in existing_questions:
                quiz.append(mq)
                existing_questions.add(mq["question"])
            if len(quiz) >= count:
                break

    # final trim in case we overshot or couldn't reach count
    quiz = quiz[:count]

    payload = {
        "url": result.url,
        "title": result.title,
        "summary": result.summary,
        "key_entities": (result.key_entities.model_dump()
                         if hasattr(result.key_entities, "model_dump")
                         else result.key_entities),
        "sections": result.sections,
        "quiz": quiz,
        "related_topics": result.related_topics,
    }

    return payload
                         
