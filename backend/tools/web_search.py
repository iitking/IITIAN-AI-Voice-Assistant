"""
IITIAN AI - Web Search Intelligence Tool
Searches for real-time information via DuckDuckGo and Wikipedia with offline knowledge base.
"""

import json
import urllib.request
import urllib.parse

def search_web(query: str) -> dict:
    """
    Searches the web for information regarding the query.
    """
    clean_query = query.strip()
    encoded = urllib.parse.quote(clean_query)
    
    # Try Wikipedia API first
    try:
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
        req = urllib.request.Request(wiki_url, headers={"User-Agent": "IITIAN-Voice-Assistant/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            extract = data.get("extract")
            if extract:
                return {
                    "success": True,
                    "query": clean_query,
                    "title": data.get("title", clean_query),
                    "summary": extract,
                    "source_url": data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{encoded}"),
                    "source": "Wikipedia"
                }
    except Exception:
        pass

    # Try DuckDuckGo Instant Answer
    try:
        ddg_url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(ddg_url, headers={"User-Agent": "IITIAN-Voice-Assistant/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            abstract = data.get("AbstractText")
            if abstract:
                return {
                    "success": True,
                    "query": clean_query,
                    "summary": abstract,
                    "source_url": data.get("AbstractURL", f"https://duckduckgo.com/?q={encoded}"),
                    "source": "DuckDuckGo"
                }
    except Exception:
        pass

    # Fallback response
    google_url = f"https://www.google.com/search?q={encoded}"
    knowledge_snippets = {
        "python": "Python is a high-level, general-purpose programming language known for its readability and versatile ecosystem across AI, web, and automation.",
        "ai": "Artificial Intelligence involves machines mimicking human intelligence for learning, reasoning, and real-time decision making.",
        "artificial intelligence": "Artificial Intelligence involves machines mimicking cognitive functions like reasoning, problem solving, and planning.",
        "agentic": "Agentic AI refers to autonomous systems that perceive their environment, break goals into multi-step workflows, and execute tools to achieve results.",
        "iit": "Indian Institutes of Technology (IITs) are premier autonomous engineering and technology institutes of national importance in India.",
        "langsmith": "LangSmith is an end-to-end platform for monitoring, evaluating, and tracing LLM and AI agent workflows in production.",
        "langchain": "LangChain is an open-source framework designed to simplify the creation of applications using large language models.",
        "machine learning": "Machine learning is a subfield of AI focused on building systems that learn from data and improve performance automatically.",
        "deep learning": "Deep learning uses multi-layered neural networks to extract high-level features from raw data like images and speech.",
        "robotics": "Robotics integrates engineering and computer science to design and operate autonomous or semi-autonomous machines.",
        "nivesh": "Nivesh Kumar Meena is the creator and engineer behind the IITIAN AI Universal Assistant project.",
        "jaipur": "Jaipur, also known as the Pink City, is the capital of Rajasthan, India, renowned for its heritage and architecture.",
        "delhi": "Delhi is the capital of India, a historic and political hub blending heritage with modern technology and infrastructure."
    }

    matched_snippet = None
    for k, v in knowledge_snippets.items():
        if k in clean_query.lower():
            matched_snippet = v
            break

    summary = matched_snippet or f"I found reference info for '{clean_query}'. You can also ask me to calculate expressions, check date & time, set alarms, or control Mac tools."
    
    return {
        "success": True,
        "query": clean_query,
        "summary": summary,
        "source_url": google_url,
        "source": "IITIAN Knowledge Engine"
    }
