#!/usr/bin/env python3
"""Local-material parsers for offer-skill v0.1."""

from __future__ import annotations

import re
from collections import Counter


TECH_KEYWORDS = {
    "python": "Python",
    "java": "Java",
    "go": "Go",
    "golang": "Go",
    "c++": "C++",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "vue": "Vue",
    "node": "Node.js",
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "redis": "Redis",
    "kafka": "Kafka",
    "rabbitmq": "RabbitMQ",
    "elasticsearch": "Elasticsearch",
    "mongodb": "MongoDB",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "linux": "Linux",
    "git": "Git",
    "微服务": "Microservices",
    "分布式": "Distributed Systems",
    "缓存": "Caching",
    "消息队列": "Message Queue",
}

SECTION_HINTS = {
    "education": {"education", "学历", "教育"},
    "experience": {"experience", "work experience", "工作经历", "经历"},
    "projects": {"project", "projects", "项目经历", "项目"},
    "skills": {"skills", "skill", "技术栈", "技能"},
}

ACTION_HINTS = (
    "built",
    "designed",
    "implemented",
    "optimized",
    "improved",
    "led",
    "owned",
    "负责",
    "设计",
    "实现",
    "优化",
    "主导",
    "搭建",
)

REQUIREMENT_HINTS = ("required", "must", "need", "要求", "熟悉", "掌握", "必须")
PLUS_HINTS = ("preferred", "plus", "加分", "优先")
RESPONSIBILITY_HINTS = ("responsibility", "职责", "工作内容", "you will", "负责")
NUMBER_HINT = re.compile(r"(\d+[%+]?|\d+\s*(?:ms|s|qps|w|万|千|k|m|亿|users))", re.IGNORECASE)
YEARS_HINT = re.compile(r"(\d+)\+?\s*(?:years?|年)", re.IGNORECASE)


def normalize_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def extract_keywords(text: str) -> list[str]:
    lowered = text.lower()
    found = []
    for raw, canonical in TECH_KEYWORDS.items():
        if raw in lowered:
            found.append(canonical)
    return sorted(set(found))


def heading_bucket(line: str) -> str | None:
    lowered = line.strip().lower().lstrip("#").strip()
    for bucket, hints in SECTION_HINTS.items():
        if lowered in hints:
            return bucket
    return None


def split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"general": []}
    current = "general"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        bucket = heading_bucket(line)
        if bucket:
            current = bucket
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def extract_claims(lines: list[str]) -> list[str]:
    claims = []
    for line in lines:
        lowered = line.lower()
        if NUMBER_HINT.search(line) or any(hint in lowered for hint in ACTION_HINTS):
            claims.append(line)
    return claims


def extract_sentences(text: str, limit: int = 5) -> list[str]:
    chunks = re.split(r"[。\n.!?]+", text)
    results = [chunk.strip() for chunk in chunks if chunk.strip()]
    return results[:limit]


def parse_resume_text(text: str) -> dict:
    sections = split_sections(text)
    all_lines = normalize_lines(text)
    years_match = YEARS_HINT.search(text)
    claims = extract_claims(all_lines)
    return {
        "source_type": "resume",
        "candidate_profile": {
            "years_of_experience": int(years_match.group(1)) if years_match else None,
        },
        "education": sections.get("education", []),
        "work_experience": sections.get("experience", []),
        "projects": sections.get("projects", []),
        "skills": extract_keywords(text),
        "claims": claims,
        "raw_sections": sections,
    }


def line_match_score(line: str, keywords: list[str]) -> int:
    lowered = line.lower()
    score = 0
    for keyword in keywords:
        if keyword.lower() in lowered:
            score += 1
    return score


def parse_jd_text(text: str) -> dict:
    lines = normalize_lines(text)
    must_have = []
    nice_to_have = []
    responsibilities = []
    role_title = lines[0] if lines else ""
    for line in lines:
        lowered = line.lower()
        if any(hint in lowered for hint in REQUIREMENT_HINTS):
            must_have.append(line)
        elif any(hint in lowered for hint in PLUS_HINTS):
            nice_to_have.append(line)
        elif any(hint in lowered for hint in RESPONSIBILITY_HINTS):
            responsibilities.append(line)

    keywords = extract_keywords(text)
    signals = {
        "system_design_weight": "high" if {"Kafka", "Redis", "Microservices", "Distributed Systems"} & set(keywords) else "medium",
        "coding_weight": "high" if {"Java", "Python", "Go", "C++"} & set(keywords) else "medium",
        "communication_weight": "medium",
    }
    return {
        "source_type": "jd",
        "role": {
            "title": role_title,
            "level": "",
            "domain": "",
        },
        "must_have": must_have,
        "nice_to_have": nice_to_have,
        "responsibilities": responsibilities,
        "keywords": keywords,
        "signals": signals,
        "raw_sections": {"general": lines},
    }


def split_project_blocks(text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#") and current:
            blocks.append(current)
            current = [line.lstrip("#").strip()]
            continue
        current.append(line)
    if current:
        blocks.append(current)
    return blocks or [normalize_lines(text)]


def infer_project_name(block: list[str], index: int) -> str:
    first = block[0].strip("#").strip()
    return first if len(first) <= 80 else f"Project {index + 1}"


def parse_projects_text(text: str) -> dict:
    projects = []
    for index, block in enumerate(split_project_blocks(text)):
        joined = "\n".join(block)
        lines = [line for line in block[1:] if line != block[0]] if block else []
        claims = extract_claims(lines or block)
        projects.append({
            "name": infer_project_name(block, index),
            "role": "",
            "context": " ".join(extract_sentences(joined, limit=2)),
            "responsibilities": [line for line in (lines or block) if any(hint in line.lower() for hint in ACTION_HINTS)][:6],
            "tech_stack": extract_keywords(joined),
            "challenges": [line for line in (lines or block) if any(hint in line.lower() for hint in ("challenge", "problem", "难点", "问题", "瓶颈"))][:5],
            "results": [line for line in claims if NUMBER_HINT.search(line)][:5],
            "claims": claims[:8],
        })
    return {
        "source_type": "projects",
        "projects": projects,
    }


def top_keywords(*keyword_lists: list[str], limit: int = 8) -> list[str]:
    counter: Counter[str] = Counter()
    for items in keyword_lists:
        counter.update(items)
    return [item for item, _count in counter.most_common(limit)]
