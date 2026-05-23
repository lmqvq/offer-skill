#!/usr/bin/env python3
"""Workflow execution helpers for offer-skill v0.1."""

from __future__ import annotations

from collections import defaultdict

from material_parser import top_keywords


DIMENSION_RULES = {
    "fundamentals": {"Java", "Python", "Go", "C++", "JavaScript", "TypeScript", "Spring Boot", "MySQL"},
    "system_design": {"Redis", "Kafka", "Microservices", "Distributed Systems", "Kubernetes", "Docker"},
    "performance": {"Redis", "Caching", "Elasticsearch"},
    "business_understanding": {"users", "growth", "conversion", "业务", "用户"},
    "ownership": {"led", "owned", "主导", "负责", "end-to-end"},
    "communication": {"collaborated", "cross-functional", "沟通", "协作", "文档"},
}


def evidence_strength(line: str) -> str:
    lowered = line.lower()
    if any(token in lowered for token in ("%", "qps", "ms", "latency", "users", "万", "千", "亿")):
        return "strong"
    if any(token in lowered for token in ("designed", "implemented", "optimized", "负责", "设计", "实现", "优化")):
        return "medium"
    return "weak"


def build_competency_map(resume: dict, projects: dict) -> dict:
    evidence_by_dimension: dict[str, list[str]] = defaultdict(list)
    lines = resume.get("claims", []) + [claim for project in projects.get("projects", []) for claim in project.get("claims", [])]
    keywords = set(resume.get("skills", []) + [item for project in projects.get("projects", []) for item in project.get("tech_stack", [])])

    for line in lines:
        lowered = line.lower()
        for dimension, rule_set in DIMENSION_RULES.items():
            if any(rule.lower() in lowered for rule in rule_set):
                evidence_by_dimension[dimension].append(line)

    for keyword in keywords:
        for dimension, rule_set in DIMENSION_RULES.items():
            if keyword in rule_set and not evidence_by_dimension[dimension]:
                evidence_by_dimension[dimension].append(f"Keyword signal: {keyword}")

    dimensions = []
    for dimension, evidence in evidence_by_dimension.items():
        strong_count = sum(1 for line in evidence if evidence_strength(line) == "strong")
        confidence = "high" if len(evidence) >= 2 else "medium"
        level = "high" if strong_count >= 1 and len(evidence) >= 2 else "medium"
        dimensions.append({
            "name": dimension,
            "level": level,
            "confidence": confidence,
            "evidence": evidence[:5],
            "gaps": [],
        })

    if not dimensions:
        dimensions.append({
            "name": "fundamentals",
            "level": "unknown",
            "confidence": "low",
            "evidence": [],
            "gaps": ["Need stronger local evidence from resume or project materials."],
        })
    return {"dimensions": dimensions}


def extract_requirement_keywords(requirement: str) -> list[str]:
    tokens = [token.strip(" ,.:;()[]").lower() for token in requirement.split()]
    return [token for token in tokens if len(token) >= 3]


def find_requirement_evidence(requirement: str, evidence_lines: list[str], keywords: list[str]) -> list[str]:
    requirement_tokens = extract_requirement_keywords(requirement)
    matches = []
    for line in evidence_lines:
        lowered = line.lower()
        if any(token in lowered for token in requirement_tokens) or any(keyword.lower() in lowered for keyword in keywords):
            matches.append(line)
    return matches[:4]


def evaluate_jd_match(resume: dict, jd: dict, projects: dict) -> dict:
    evidence_lines = resume.get("claims", []) + resume.get("work_experience", []) + [claim for project in projects.get("projects", []) for claim in project.get("claims", [])]
    resume_keywords = top_keywords(resume.get("skills", []), [item for project in projects.get("projects", []) for item in project.get("tech_stack", [])])

    must_have_results = []
    gaps = []
    weak = []
    for requirement in jd.get("must_have", []) or jd.get("keywords", []):
        evidence = find_requirement_evidence(requirement, evidence_lines, resume_keywords)
        if evidence:
            strong = any(evidence_strength(item) == "strong" for item in evidence)
            status = "matched" if strong or len(evidence) >= 2 else "weak_evidence"
            payload = {
                "requirement": requirement,
                "status": status,
                "evidence": evidence,
            }
            must_have_results.append(payload)
            if status == "weak_evidence":
                weak.append(payload)
        else:
            gaps.append({
                "requirement": requirement,
                "status": "missing_evidence",
                "evidence": [],
            })

    strong_count = sum(1 for item in must_have_results if item["status"] == "matched")
    if strong_count >= 3 and not gaps:
        overall = "high"
    elif strong_count >= 1:
        overall = "medium"
    else:
        overall = "low"

    risk_flags = []
    if not resume.get("claims"):
        risk_flags.append("Resume claims are thin; stronger quantified evidence is needed.")
    if gaps:
        risk_flags.append("Some JD requirements have no direct local evidence.")
    if weak:
        risk_flags.append("Several matches exist but are not strongly evidenced in the materials.")

    return {
        "overall_match": overall,
        "must_have_match": must_have_results,
        "weak_matches": weak,
        "gaps": gaps,
        "risk_flags": risk_flags,
    }


def build_question_bank(jd_match: dict, projects: dict) -> dict:
    questions = []
    index = 1

    for weak in jd_match.get("weak_matches", []):
        questions.append({
            "id": f"q_resume_{index:03d}",
            "category": "resume-validation",
            "difficulty": "medium",
            "question": f"你在简历中体现了“{weak['requirement']}”，能结合一个具体项目说明你真正负责了什么吗？",
            "intent": "验证弱证据要求是否真实落地",
            "expected_signals": [
                "能给出具体场景",
                "能说明本人贡献",
                "能解释结果或取舍",
            ],
            "follow_ups": [
                "如果当时失败，你会怎么定位问题？"
            ],
            "source": {
                "type": "generated",
                "workflow": "resume-eval",
            },
        })
        index += 1

    for gap in jd_match.get("gaps", [])[:3]:
        questions.append({
            "id": f"q_resume_{index:03d}",
            "category": "gap-check",
            "difficulty": "medium",
            "question": f"JD 里强调“{gap['requirement']}”，你的相关经验主要来自哪里？",
            "intent": "确认是否完全缺失或只是简历未展开",
            "expected_signals": [
                "能承认边界或补充真实经历",
                "不会用空泛术语回避",
            ],
            "follow_ups": [
                "如果经验有限，你会如何快速补齐？"
            ],
            "source": {
                "type": "generated",
                "workflow": "resume-eval",
            },
        })
        index += 1

    for project in projects.get("projects", [])[:2]:
        if project.get("challenges") or project.get("results"):
            questions.append({
                "id": f"q_project_{index:03d}",
                "category": "project-deep-dive",
                "difficulty": "medium",
                "question": f"在项目“{project['name']}”里，最值得深挖的技术难点是什么？",
                "intent": "验证项目深度和问题拆解能力",
                "expected_signals": [
                    "能讲清背景与约束",
                    "能解释方案和取舍",
                ],
                "follow_ups": [
                    "如果把流量放大 10 倍，原方案会先坏在哪里？"
                ],
                "source": {
                    "type": "generated",
                    "workflow": "project-highlight",
                },
            })
            index += 1

    return {"questions": questions}


def markdown_list(items: list[str], empty_fallback: str) -> str:
    if not items:
        return f"- {empty_fallback}"
    return "\n".join(f"- {item}" for item in items)


def render_resume_eval(meta: dict, resume: dict, jd: dict, jd_match: dict, question_bank: dict) -> str:
    strong_matches = [item["requirement"] for item in jd_match.get("must_have_match", []) if item["status"] == "matched"]
    weak_matches = [item["requirement"] for item in jd_match.get("weak_matches", [])]
    missing = [item["requirement"] for item in jd_match.get("gaps", [])]
    candidate_suggestions = []
    if weak_matches:
        candidate_suggestions.append("Expand weak matches with one concrete project story each.")
    if missing:
        candidate_suggestions.append("Acknowledge missing areas directly and prepare a learning plan instead of over-claiming.")
    if not candidate_suggestions:
        candidate_suggestions.append("Keep the strongest evidence near the top of the resume and interview narrative.")

    interviewer_questions = [item["question"] for item in question_bank.get("questions", [])[:5]]
    return f"""# Resume Evaluation

## Overall Match
- Perspective: {meta.get('perspective', 'candidate')}
- Overall match: {jd_match.get('overall_match', 'unknown')}
- Scope note: v0.1 is local-only and does not use live web research.

## Strong Matches
{markdown_list(strong_matches, "No strong matches detected yet from local evidence.")}

## Weak Matches
{markdown_list(weak_matches, "No weak-but-present matches detected.")}

## Missing Evidence
{markdown_list(missing, "No explicit missing evidence detected from the current JD parse.")}

## Candidate Suggestions
{markdown_list(candidate_suggestions, "Add stronger quantified results and clearer ownership statements.")}

## Interviewer Questions
{markdown_list(interviewer_questions, "No interviewer questions generated yet.")}

## Final Notes
- Risk flags:
{markdown_list(jd_match.get('risk_flags', []), "No additional risk flags.")}
- Deferred workflows remain planned after v0.1: `mock-interview`, `interview-retro`.
"""


def render_project_highlight(meta: dict, projects: dict, competency_map: dict, question_bank: dict) -> str:
    project = projects.get("projects", [{}])[0] if projects.get("projects") else {}
    results = project.get("results", [])
    responsibilities = project.get("responsibilities", [])
    challenges = project.get("challenges", [])
    tech_stack = project.get("tech_stack", [])
    risk_flags = []
    if not results:
        risk_flags.append("The project notes do not yet show quantified outcomes.")
    if not responsibilities:
        risk_flags.append("Ownership is still vague; add concrete responsibilities.")
    if not challenges:
        risk_flags.append("Technical challenges are not explicit yet.")

    candidate_view = []
    if responsibilities:
        candidate_view.append("Lead with your concrete ownership before naming the tech stack.")
    if results:
        candidate_view.append("Use measurable impact early to avoid sounding like a feature tour.")
    if challenges:
        candidate_view.append("Explain one real tradeoff or bottleneck instead of listing every implementation detail.")
    if not candidate_view:
        candidate_view.append("Add stronger local detail before using this case in an interview.")

    interviewer_view = []
    if tech_stack:
        interviewer_view.append("Probe whether the candidate can connect the stack to an actual production constraint.")
    if results:
        interviewer_view.append("Verify whether the candidate can explain how the impact was measured.")
    if challenges:
        interviewer_view.append("Push on the hardest challenge to separate surface familiarity from real ownership.")
    if not interviewer_view:
        interviewer_view.append("The current material is too thin for a high-confidence project assessment.")

    suggested_questions = [item["question"] for item in question_bank.get("questions", []) if item["source"]["workflow"] == "project-highlight"][:5]
    top_dimensions = [item["name"] for item in competency_map.get("dimensions", [])]
    summary_bits = [project.get("name", "Primary Project")]
    if tech_stack:
        summary_bits.append(" / ".join(tech_stack[:4]))
    if top_dimensions:
        summary_bits.append("signals: " + ", ".join(top_dimensions[:3]))

    return f"""# Project Highlight

## Summary
- Perspective: {meta.get('perspective', 'candidate')}
- Project: {project.get('name', 'Primary Project')}
- Snapshot: {' | '.join(summary_bits)}
- Scope note: v0.1 is local-only and does not include web-assisted interview research.

## Candidate View
{markdown_list(candidate_view, "Add clearer project framing and stronger personal ownership.")}

## Interviewer View
{markdown_list(interviewer_view, "Need more evidence before interviewer-side judgment is meaningful.")}

## Evidence
{markdown_list(results + responsibilities[:4], "No strong project evidence extracted yet.")}

## Risk Flags
{markdown_list(risk_flags, "No immediate risk flags.")}

## Suggested Questions
{markdown_list(suggested_questions, "No project-deep-dive questions generated yet.")}

## Action Items
{markdown_list([
    "Add one quantified outcome if available.",
    "Clarify your exact ownership boundary.",
    "Keep deferred workflows visible: `mock-interview`, `interview-retro`."
], "Add clearer evidence and ownership details.")}
"""
