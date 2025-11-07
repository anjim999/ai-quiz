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
            "Follow this schema exactly:\n{format_instructions}\n"
        ),
        input_variables=["url", "title", "article_text"],
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

def generate_quiz_payload(url: str, title: str, article_text: str, sections: list[str]) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        return _fallback_quiz(url, title, article_text, sections)

    chain = ensure_chain()
    result: QuizOutput = chain.invoke({
        "url": url,
        "title": title,
        "article_text": article_text,
    })

    payload = {
        "url": result.url,
        "title": result.title,
        "summary": result.summary,
        "key_entities": (result.key_entities.model_dump()
                         if hasattr(result.key_entities, "model_dump")
                         else result.key_entities),
        "sections": result.sections,
        "quiz": [q.model_dump() for q in result.quiz],
        "related_topics": result.related_topics,
    }
    return payload
