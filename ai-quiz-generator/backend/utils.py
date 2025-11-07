import re
from urllib.parse import urlparse

WIKI_HOSTS = {"wikipedia.org"}
URL_RE = re.compile(r"^https?://[\w.-]+(/[\w\-./%?#=&+]*)?$")

def is_wikipedia_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        return any(host.endswith(h) for h in WIKI_HOSTS) and "/wiki/" in parsed.path
    except Exception:
        return False
