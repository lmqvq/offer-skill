#!/usr/bin/env python3
"""Workflow execution helpers for offer-skill."""

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
UNKNOWN_ANSWER_HINTS = ("not sure", "don't know", "不知道", "不太清楚", "忘了", "没做过")


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


def merge_question_banks(*question_banks: dict) -> dict:
    merged = []
    seen = set()
    for bank in question_banks:
        for question in bank.get("questions", []):
            key = question.get("question", "")
            if key and key not in seen:
                merged.append(question)
                seen.add(key)
    return {"questions": merged}


def build_research_question_bank(research_bundle: dict) -> dict:
    questions = []
    for index, question in enumerate(research_bundle.get("question_candidates", [])[:8], start=1):
        questions.append({
            "id": f"q_research_{index:03d}",
            "category": "market-trend",
            "difficulty": "medium" if research_bundle.get("profile") == "web-assisted" else "high",
            "question": question,
            "intent": "Reflect recent external interview themes and repeated question patterns.",
            "expected_signals": [
                "能回答当前主流面试关注点",
                "能结合真实项目而不是只背题",
            ],
            "follow_ups": [
                "这类问题如果落到你的项目里，会映射到哪里？"
            ],
            "source": {
                "type": "research",
                "workflow": "mock-interview",
                "profile": research_bundle.get("profile", "local-only"),
            },
        })
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
- Research profile: {meta.get('research', {}).get('profile', 'local-only')}

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
- This output can be chained into `mock-interview` or `interview-retro`.
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
- Research profile: {meta.get('research', {}).get('profile', 'local-only')}

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
    "Prepare one interviewer-style deep-dive answer for the hardest challenge."
], "Add clearer evidence and ownership details.")}
"""


def categorize_question(question: str) -> str:
    lowered = question.lower()
    if any(token in lowered for token in ("project", "项目", "负责", "ownership")):
        return "project"
    if any(token in lowered for token in ("design", "架构", "系统", "并发", "distributed", "cache")):
        return "system"
    if any(token in lowered for token in ("why", "tradeoff", "取舍", "latency", "performance", "优化")):
        return "deep-dive"
    return "fundamentals"


def render_mock_interview(
    meta: dict,
    jd_match: dict,
    question_bank: dict,
    research_bundle: dict | None = None,
) -> str:
    grouped: dict[str, list[str]] = defaultdict(list)
    for item in question_bank.get("questions", []):
        grouped[categorize_question(item["question"])].append(item["question"])

    failure_modes = []
    if jd_match.get("gaps"):
        failure_modes.append("Candidate may struggle where JD requirements lack direct evidence.")
    if jd_match.get("weak_matches"):
        failure_modes.append("Candidate may sound familiar with the topic but fail under follow-up questions.")
    if research_bundle and research_bundle.get("trend_topics"):
        failure_modes.append("Recent external themes may expose gaps outside the candidate's prepared local stories.")
    if not failure_modes:
        failure_modes.append("Primary failure risk is generic, non-evidence-based answering.")

    practice_plan = [
        "Answer the first 3 questions out loud with one concrete project story each.",
        "Prepare one metric, one tradeoff, and one failure case for your strongest project.",
    ]
    if research_bundle and research_bundle.get("trend_topics"):
        practice_plan.append("Review the extracted trend topics and map each one to your own project evidence before the interview.")

    trend_lines = research_bundle.get("trend_topics", []) if research_bundle else []
    question_sections = []
    ordered_categories = ("fundamentals", "project", "system", "deep-dive", "market-trend")
    for category in ordered_categories:
        questions = grouped.get(category, [])
        if questions:
            question_sections.append(f"### {category.title()}\n" + "\n".join(f"- {item}" for item in questions[:4]))
    question_block = "\n\n".join(question_sections) if question_sections else "- No questions generated."

    return f"""# Mock Interview

## Interview Setup
- Perspective: {meta.get('perspective', 'candidate')}
- Research profile: {meta.get('research', {}).get('profile', 'local-only')}
- Match level: {jd_match.get('overall_match', 'unknown')}

## Question List
{question_block}

## Expected Signals
- Concrete project ownership
- Clear tradeoff reasoning
- Measurable outcomes where available
- Ability to handle follow-up pressure

## Common Failure Modes
{markdown_list(failure_modes, "No failure modes identified.")}

## Follow-up Paths
- Ask the candidate to move from summary to exact ownership.
- Push on one technical tradeoff, one bottleneck, and one failure scenario.
- If the answer is generic, force a concrete project example.

## Practice Plan
{markdown_list(practice_plan, "Practice the top local questions first.")}

## Research Signals
{markdown_list(trend_lines, "No external trend signals were used.")}
"""


def evaluate_interview_rounds(interview_notes: dict, candidate_answers: dict | None = None) -> dict:
    qa_pairs = []
    answer_lookup = {}
    if candidate_answers:
        for item in candidate_answers.get("answers", []):
            if item.get("question"):
                answer_lookup[item["question"]] = item.get("answer", "")

    for round_item in interview_notes.get("rounds", []):
        for question in round_item.get("questions", []):
            answer = answer_lookup.get(question.get("question", ""), question.get("candidate_answer_summary", ""))
            qa_pairs.append({
                "question": question.get("question", ""),
                "answer": answer.strip(),
            })

    wins = []
    weak = []
    expression = []
    for pair in qa_pairs:
        answer = pair["answer"]
        lowered = answer.lower()
        if any(token in lowered for token in UNKNOWN_ANSWER_HINTS):
            weak.append(pair["question"])
        elif len(answer) < 24:
            expression.append(pair["question"])
        elif evidence_strength(answer) in {"strong", "medium"}:
            wins.append(pair["question"])
        else:
            expression.append(pair["question"])

    return {
        "qa_pairs": qa_pairs,
        "wins": wins,
        "weak": weak,
        "expression": expression,
    }


def render_interview_retro(
    meta: dict,
    retro_eval: dict,
    jd_match: dict | None = None,
    research_bundle: dict | None = None,
) -> str:
    improvement_plan = []
    if retro_eval.get("weak"):
        improvement_plan.append("For weak questions, prepare direct knowledge-gap remediation and one stronger project example.")
    if retro_eval.get("expression"):
        improvement_plan.append("For short or vague answers, rehearse a clearer structure: context -> action -> tradeoff -> result.")
    if jd_match and jd_match.get("gaps"):
        improvement_plan.append("Map the JD gap list to practice answers before the next round.")
    if research_bundle and research_bundle.get("trend_topics"):
        improvement_plan.append("Compare your weak areas against the extracted trend topics and prioritize overlap first.")
    if not improvement_plan:
        improvement_plan.append("Keep practicing with role-specific follow-ups and stronger evidence density.")

    next_questions = []
    for item in retro_eval.get("weak", [])[:3] + retro_eval.get("expression", [])[:2]:
        next_questions.append(f"Redo this question with a stronger answer: {item}")
    if not next_questions:
        next_questions.append("Repeat your strongest answer and compress it into a sharper 60-second version.")

    trend_lines = research_bundle.get("trend_topics", []) if research_bundle else []
    return f"""# Interview Retrospective

## Summary
- Perspective: {meta.get('perspective', 'dual')}
- Reviewed questions: {len(retro_eval.get('qa_pairs', []))}
- Wins: {len(retro_eval.get('wins', []))}
- Knowledge gaps: {len(retro_eval.get('weak', []))}
- Expression gaps: {len(retro_eval.get('expression', []))}

## What Went Well
{markdown_list(retro_eval.get('wins', []), "No clear strengths were detected from the provided notes.")}

## What Broke Down
{markdown_list(retro_eval.get('weak', []) + retro_eval.get('expression', []), "No major breakdowns detected.")}

## Interviewer Interpretation
{markdown_list([
    "Weak-answer questions likely reduce confidence in depth.",
    "Short or generic answers may be read as shallow ownership even when the candidate knows the topic.",
    "The interviewer will usually follow the weakest evidence path, not the strongest resume line."
], "No interviewer interpretation available.")}

## Candidate Improvement Plan
{markdown_list(improvement_plan, "Keep practicing clearer, evidence-backed answers.")}

## Next Practice Questions
{markdown_list(next_questions, "No next questions suggested.")}

## Research Signals
{markdown_list(trend_lines, "No external trend signals were used.")}
"""
