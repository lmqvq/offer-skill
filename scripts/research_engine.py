#!/usr/bin/env python3
"""Research helpers for offer-skill web-assisted and deep-research modes."""

from __future__ import annotations

import re
from collections import Counter
from html import unescape
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from common import write_json, write_text


USER_AGENT = "offer-skill/1.0 (+https://github.com/lmqvq/offer-skill)"
QUESTION_PATTERN = re.compile(r"([^。！？\n]{6,120}[?？])")


def strip_tags(html: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return unescape(text).strip()


def search_duckduckgo(query: str, limit: int = 5) -> list[dict]:
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=10) as response:
        html = response.read().decode("utf-8", errors="ignore")

    pattern = re.compile(
        r'<a[^>]*class="result__a"[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    results = []
    for match in pattern.finditer(html):
        title = strip_tags(match.group("title"))
        url = unescape(match.group("url"))
        if title and url:
            results.append({"title": title, "url": url})
        if len(results) >= limit:
            break
    return results


def fetch_url_text(url: str, max_chars: int = 4000) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=10) as response:
        html = response.read().decode("utf-8", errors="ignore")
    return strip_tags(html)[:max_chars]


def extract_question_candidates(text: str, limit: int = 12) -> list[str]:
    matches = [match.strip() for match in QUESTION_PATTERN.findall(text)]
    unique = []
    seen = set()
    for item in matches:
        if item not in seen:
            unique.append(item)
            seen.add(item)
        if len(unique) >= limit:
            break
    return unique


def extract_trend_topics(texts: list[str], limit: int = 8) -> list[str]:
    counter: Counter[str] = Counter()
    for text in texts:
        lowered = text.lower()
        for token in (
            "redis",
            "kafka",
            "mysql",
            "system design",
            "microservice",
            "distributed",
            "performance",
            "cache",
            "项目",
            "设计",
            "并发",
            "数据库",
            "消息队列",
            "稳定性",
            "高并发",
        ):
            if token in lowered:
                counter[token] += 1
    return [topic for topic, _count in counter.most_common(limit)]


def derive_queries(role_title: str, stack: list[str], explicit_query: str | None, profile: str) -> list[str]:
    if explicit_query:
        return [explicit_query]
    base = role_title or "software engineer"
    stack_suffix = " ".join(stack[:3]) if stack else ""
    queries = [f"{base} {stack_suffix} interview experience".strip()]
    if profile == "deep-research":
        queries.extend([
            f"{base} {stack_suffix} common interview questions".strip(),
            f"{base} {stack_suffix} system design interview".strip(),
        ])
    return queries


def render_research_summary(bundle: dict) -> str:
    topics = bundle.get("trend_topics", [])
    questions = bundle.get("question_candidates", [])
    sources = bundle.get("sources", [])
    source_lines = "\n".join(
        f"- {item.get('title', 'unknown')} {item.get('url', '')}".strip()
        for item in sources[:8]
    ) or "- No external sources captured."
    topic_lines = "\n".join(f"- {item}" for item in topics) or "- No trend topics extracted."
    question_lines = "\n".join(f"- {item}" for item in questions[:8]) or "- No question candidates extracted."
    return f"""# Research Summary

## Profile
- {bundle.get('profile', 'local-only')}

## Queries
{chr(10).join(f"- {query}" for query in bundle.get('queries', [])) or "- None"}

## Sources
{source_lines}

## Trend Topics
{topic_lines}

## Candidate Questions
{question_lines}
"""


def build_research_bundle(
    *,
    case_dir: Path,
    profile: str,
    role_title: str,
    stack: list[str],
    explicit_query: str | None = None,
    research_text: str | None = None,
) -> dict:
    raw_sources = []
    texts = []
    queries = derive_queries(role_title, stack, explicit_query, profile)

    if research_text:
        raw_sources.append({
            "title": "provided-research-notes",
            "url": "",
            "text": research_text[:4000],
            "source_type": "provided-text",
        })
        texts.append(research_text)

    if profile in {"web-assisted", "deep-research"}:
        per_query_limit = 3 if profile == "web-assisted" else 5
        for query in queries:
            try:
                results = search_duckduckgo(query, limit=per_query_limit)
            except Exception as exc:  # pragma: no cover
                raw_sources.append({
                    "title": f"search-error:{query}",
                    "url": "",
                    "text": str(exc),
                    "source_type": "search-error",
                })
                continue
            for result in results:
                source = {
                    "title": result["title"],
                    "url": result["url"],
                    "text": "",
                    "source_type": "web-search",
                }
                if profile == "deep-research":
                    try:
                        source["text"] = fetch_url_text(result["url"])
                    except Exception as exc:  # pragma: no cover
                        source["text"] = f"fetch-error: {exc}"
                raw_sources.append(source)
                texts.append(source["text"] or source["title"])

    question_candidates = []
    for text in texts:
        question_candidates.extend(extract_question_candidates(text))
    unique_questions = []
    seen = set()
    for item in question_candidates:
        if item not in seen:
            unique_questions.append(item)
            seen.add(item)

    bundle = {
        "profile": profile,
        "queries": queries,
        "sources": raw_sources,
        "trend_topics": extract_trend_topics(texts),
        "question_candidates": unique_questions[:12],
        "source_count": len(raw_sources),
    }
    write_json(case_dir / "research" / "raw" / f"{profile}-research.json", bundle)
    write_text(case_dir / "research" / "merged" / f"{profile}-summary.md", render_research_summary(bundle))
    return bundle
