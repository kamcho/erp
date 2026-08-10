"""
KICD CBE Senior School pathway inference from subject performance.

Pathways (Senior School):
  - STEM
  - Social Sciences
  - Arts and Sports Science
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

PATHWAYS = (
    {
        "key": "stem",
        "name": "STEM",
        "full_name": "Science, Technology, Engineering & Mathematics",
        "icon": "fa-flask",
        "color": "indigo",
        "description": "Strong fit for science, mathematics, technology, and applied technical disciplines.",
    },
    {
        "key": "social",
        "name": "Social Sciences",
        "full_name": "Social Sciences",
        "icon": "fa-landmark",
        "color": "sky",
        "description": "Strong fit for languages, humanities, business, and social studies.",
    },
    {
        "key": "arts",
        "name": "Arts & Sports",
        "full_name": "Arts and Sports Science",
        "icon": "fa-palette",
        "color": "amber",
        "description": "Strong fit for creative arts, performing arts, and sports science.",
    },
)

PATHWAY_BY_KEY = {p["key"]: p for p in PATHWAYS}

# Course (learning area) → default pathway
COURSE_PATHWAY = {
    "Mathematics & Science": "stem",
    "Technical & Applied": "stem",
    "Language & Communication": "social",
    "Environment & Social": "social",
    "Religious & Moral": "social",
    "Creative & Psychomotor": "arts",
}

# Subject-name overrides checked first (more specific → pathway)
SUBJECT_PATHWAY_KEYWORDS = (
    # Arts & Sports (check before STEM "health" matches)
    (("physical and health", "physical education", "sports", "creative arts",
      "visual art", "performing", "music", "psychomotor", "movement and creative"), "arts"),
    # STEM
    (("mathematics", "math", "integrated science", "biology", "chemistry",
      "physics", "computer", "agriculture", "pre-technical", "home science",
      "health education", "hygiene", "science and technology", "engineering"), "stem"),
    # Social Sciences
    (("english", "kiswahili", "language", "social studies", "history", "geography",
      "religious", "cre", "ire", "business", "life skills", "civic"), "social"),
)


def pathway_for_subject(subject) -> str:
    """Return pathway key for a Subject instance."""
    name = (getattr(subject, "name", "") or "").strip().lower()
    for keywords, key in SUBJECT_PATHWAY_KEYWORDS:
        if any(k in name for k in keywords):
            return key

    course = getattr(subject, "course", None)
    course_name = getattr(course, "name", "") if course else ""
    if course_name in COURSE_PATHWAY:
        return COURSE_PATHWAY[course_name]

    # Business Studies is TEC course but Social Sciences pathway at senior school
    if "business" in name:
        return "social"
    return "social"


def infer_cbe_pathway(exam_scores: list[Any]) -> dict[str, Any]:
    """
    Infer KICD pathway from a list of score-like objects with:
      .subject, .percentage (0-100), optional .points, .grade, .score, .max_score
    """
    buckets: dict[str, list[dict]] = defaultdict(list)

    for item in exam_scores:
        subject = getattr(item, "subject", None)
        if subject is None:
            continue
        perc = float(getattr(item, "percentage", 0) or 0)
        key = pathway_for_subject(subject)
        buckets[key].append({
            "name": subject.name,
            "percentage": round(perc, 1),
            "grade": getattr(item, "grade", None),
            "points": getattr(item, "points", None),
            "course": getattr(getattr(subject, "course", None), "name", "") or "",
        })

    pathway_rows = []
    for meta in PATHWAYS:
        key = meta["key"]
        subjects = sorted(buckets.get(key, []), key=lambda s: s["percentage"], reverse=True)
        avg = round(sum(s["percentage"] for s in subjects) / len(subjects), 1) if subjects else 0.0
        pathway_rows.append({
            **meta,
            "average": avg,
            "subject_count": len(subjects),
            "subjects": subjects,
            "top_subjects": subjects[:3],
        })

    scored = [p for p in pathway_rows if p["subject_count"] > 0]
    if not scored:
        return {
            "has_data": False,
            "recommended": None,
            "pathways": pathway_rows,
            "confidence": 0,
            "rationale": "No exam scores available to infer a pathway yet.",
        }

    # Prefer strong averages with enough subject evidence (breadth matters for pathway fit)
    for p in scored:
        p["fitness"] = round(
            p["average"] * (1 + 0.12 * max(0, p["subject_count"] - 1)),
            2,
        )

    scored.sort(key=lambda p: (p["fitness"], p["average"], p["subject_count"]), reverse=True)
    recommended = scored[0]
    runner_up = scored[1] if len(scored) > 1 else None
    gap = recommended["fitness"] - (runner_up["fitness"] if runner_up else 0)

    # Confidence: strength of average + separation from next pathway
    confidence = min(98, int(round(recommended["average"] * 0.55 + gap * 1.2 + 15)))
    if recommended["subject_count"] < 2:
        confidence = max(35, confidence - 15)

    top_names = ", ".join(s["name"] for s in recommended["top_subjects"][:2]) or "core subjects"
    rationale = (
        f"Based on current exam performance, {recommended['full_name']} is the strongest fit "
        f"(avg {recommended['average']}%). Leading subjects: {top_names}."
    )
    if runner_up and gap < 5:
        rationale += (
            f" Close alternative: {runner_up['name']} "
            f"({runner_up['average']}%)."
        )

    # Normalize bar widths relative to max average among scored pathways
    max_avg = max(p["average"] for p in scored) or 1
    for p in pathway_rows:
        p["bar_width"] = int(round((p["average"] / max_avg) * 100)) if p["average"] else 0
        p["is_recommended"] = p["key"] == recommended["key"]

    return {
        "has_data": True,
        "recommended": recommended,
        "pathways": pathway_rows,
        "confidence": confidence,
        "rationale": rationale,
        "exam_label": None,
    }
