import requests
from bs4 import BeautifulSoup
from typing import Tuple

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
MAIN_SELECTOR = "#mw-content-text .mw-parser-output"

def clean_wikipedia_html(html: str) -> Tuple[str, str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find(id="firstHeading")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"

    main = soup.select_one(MAIN_SELECTOR)
    if not main:
        return title, html, ""

    for sel in ["table", "style", "script", "noscript", "figure",
                "span.mw-editsection", "div.navbox", "div.reflist",
                "ol.references", "sup.reference"]:
        for tag in main.select(sel):
            tag.decompose()

    parts = []
    for p in main.find_all(["p", "li"]):
        text = p.get_text(" ", strip=True)
        if text:
            parts.append(text)
    text_out = "\n".join(parts)
    return title, str(main), text_out

def scrape_wikipedia(url: str) -> tuple[str, str, list[str], str]:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    title, cleaned_html, cleaned_text = clean_wikipedia_html(resp.text)

    soup = BeautifulSoup(cleaned_html, "html.parser")
    sections = []
    for hdr in soup.find_all(["h2", "h3"]):
        sec_title = hdr.get_text(" ", strip=True).replace("[edit]", "").strip()
        if sec_title:
            sections.append(sec_title)
    return title, cleaned_text, sections, resp.text
