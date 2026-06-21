"""Gap Assessment Report Generator — Domain scores, maturity ratings, remediation.

Produces a structured compliance report from the completed assessment state.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

from app.gap_assessment.question_bank import (
    ALL_QUESTIONS,
    DOMAINS,
    DOMAIN_QUESTIONS,
    Question,
)
from app.gap_assessment.wizard_engine import (
    AssessmentState,
    compute_domain_scores,
    compute_overall_score,
)

logger = logging.getLogger(__name__)

# Maturity rating thresholds
_MATURITY_LEVELS = {
    "Initial": (0, 20),
    "Developing": (20, 40),
    "Defined": (40, 60),
    "Managed": (60, 80),
    "Optimised": (80, 100),
}

# Remediation suggestions keyed by question ID
REMEDIATION = {
    "IR-01": "Draft a 2-page incident response plan covering detection, containment, recovery, and notification. Assign an incident lead and define escalation paths. Start with your highest-risk scenarios.",
    "IR-02": "Form a 3-5 person IRT with a designated lead, technical analyst, and communications coordinator. Document their roles and contact information.",
    "IR-03": "Set up a contact list and draft a template notification for NTA. Test the process with a tabletop exercise.",
    "IR-04": "Schedule a quarterly tabletop exercise. Use NIST SP 800-61 scenarios or create one based on your highest-risk threats.",
    "IR-05": "Establish evidence collection procedures. Designate a storage location for forensic data and define chain-of-custody rules.",
    "DP-01": "Implement consent collection in all data entry points. Use clear language, unchecked checkboxes, and record timestamps. Review the Individual Privacy Act 2075 §5-6.",
    "DP-02": "Create a data retention schedule mapping each data category to a retention period. Implement automated deletion where possible.",
    "DP-03": "Build a self-service portal or documented process for data subject access requests (DSARs). Set a 30-day response SLA.",
    "DP-04": "Appoint a DPO or privacy lead. Register with the Privacy Commission if processing sensitive data at scale.",
    "DP-05": "Create a breach notification template and contact list. Define the 72-hour escalation process. Test annually.",
    "AC-01": "Map each role to the minimum permissions required. Document the mapping and review it quarterly.",
    "AC-02": "Enable MFA on all admin accounts, cloud services, and customer portals. Use authenticator apps over SMS where possible.",
    "AC-03": "Implement a quarterly access review process. Use automated tooling where available. Document and retain audit evidence.",
    "AC-04": "Create a formal joiner/mover/leaver process. Integrate with HR systems for automated provisioning/deprovisioning.",
    "AC-05": "Deploy a PAM solution for admin accounts. Enable session recording and just-in-time access for elevated privileges.",
    "SA-01": "Create a 30-minute onboarding security training module. Cover phishing, passwords, data handling, and incident reporting.",
    "SA-02": "Develop annual refresher content addressing current threat landscape. Use interactive formats (videos, quizzes).",
    "SA-03": "Run monthly or quarterly simulated phishing campaigns. Track click rates and reporting rates as KPIs.",
    "SA-04": "Create role-specific training tracks: developers (secure coding), executives (governance), general staff (basics).",
    "SA-05": "Implement an LMS or spreadsheet to track completion. Generate reports for audit evidence.",
    "TPR-01": "Build a vendor inventory with data sensitivity classifications. Include cloud providers, SaaS tools, and outsourced services.",
    "TPR-02": "Create a vendor risk assessment questionnaire. Score vendors by data sensitivity and access level. Prioritise high-risk vendors.",
    "TPR-03": "Add standard security clauses to all contracts: data protection obligations, incident reporting timelines, audit rights, and termination procedures.",
    "TPR-04": "Implement annual vendor reviews for high-risk vendors. Track remediation of identified issues.",
    "TPR-05": "Create a vendor offboarding checklist: revoke access, return assets, confirm data deletion, document completion.",
}


@dataclass
class DomainReport:
    """Report section for a single compliance domain."""
    domain_code: str
    domain_name: str
    score: float  # 0-100
    maturity: str
    questions_answered: int
    total_questions: int
    gaps: list[dict] = field(default_factory=list)  # question + answer + remediation


@dataclass
class ComplianceReport:
    """Full compliance gap-assessment report."""
    session_id: str
    overall_score: float
    overall_maturity: str
    domain_reports: list[DomainReport]
    total_questions: int
    total_answered: int
    strengths: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)


def _maturity_label(score: float) -> str:
    """Map a 0-100 score to a maturity level label."""
    for label, (low, high) in _MATURITY_LEVELS.items():
        if low <= score < high:
            return label
    return "Optimised"


def generate_report(state: AssessmentState) -> ComplianceReport:
    """Generate a full compliance report from a completed assessment state."""
    domain_scores = compute_domain_scores(state)
    overall = compute_overall_score(state)

    domain_reports: list[DomainReport] = []
    all_gaps: list[tuple[float, str]] = []  # (score, priority_text)

    for domain_code, questions in DOMAIN_QUESTIONS.items():
        score = domain_scores.get(domain_code, 0.0)
        maturity = _maturity_label(score)

        gaps: list[dict] = []
        for q in questions:
            answer = state.answers.get(q.id, "No")
            if answer != "Yes":
                gaps.append({
                    "question_id": q.id,
                    "question": q.text,
                    "answer": answer,
                    "score": _score_value(answer),
                    "remediation": REMEDIATION.get(q.id, "Review the applicable regulatory requirements."),
                    "regulatory_ref": q.regulatory_ref,
                })

        domain_reports.append(DomainReport(
            domain_code=domain_code,
            domain_name=DOMAINS[domain_code],
            score=score,
            maturity=maturity,
            questions_answered=sum(1 for q in questions if q.id in state.answers),
            total_questions=len(questions),
            gaps=gaps,
        ))

        # Collect priorities (domains below 60%)
        if score < 60:
            all_gaps.append((score, f"{DOMAINS[domain_code]} ({score}%) — {len(gaps)} gaps to address"))

    # Sort priorities by score (lowest first)
    all_gaps.sort(key=lambda x: x[0])
    priorities = [text for _, text in all_gaps]

    # Strengths: domains above 80%
    strengths = [
        f"{DOMAINS[dc]} ({score}%)"
        for dc, score in domain_scores.items()
        if score >= 80
    ]

    return ComplianceReport(
        session_id=state.session_id,
        overall_score=overall,
        overall_maturity=_maturity_label(overall),
        domain_reports=domain_reports,
        total_questions=len(ALL_QUESTIONS),
        total_answered=len(state.answers),
        strengths=strengths,
        priorities=priorities,
    )


def _score_value(answer: str) -> float:
    return {"Yes": 1.0, "Partially": 0.5, "No": 0.0}.get(answer, 0.0)


def format_report_text(report: ComplianceReport) -> str:
    """Format a compliance report as human-readable text."""
    lines = [
        "=" * 60,
        "COMPLIANCE GAP-ASSESSMENT REPORT",
        f"Session: {report.session_id}",
        "=" * 60,
        "",
        f"Overall Score: {report.overall_score}% — Maturity: {report.overall_maturity}",
        f"Questions Answered: {report.total_answered}/{report.total_questions}",
        "",
    ]

    if report.strengths:
        lines.append("STRENGTHS:")
        for s in report.strengths:
            lines.append(f"  ✓ {s}")
        lines.append("")

    if report.priorities:
        lines.append("PRIORITY AREAS:")
        for p in report.priorities:
            lines.append(f"  ✗ {p}")
        lines.append("")

    lines.append("-" * 60)
    lines.append("DOMAIN DETAILS:")
    lines.append("")

    for dr in report.domain_reports:
        lines.append(f"  {dr.domain_name} — {dr.score}% ({dr.maturity})")
        lines.append(f"  Questions: {dr.questions_answered}/{dr.total_questions}")
        if dr.gaps:
            lines.append("  Gaps:")
            for g in dr.gaps:
                lines.append(f"    [{g['question_id']}] {g['answer']}")
                lines.append(f"      {g['question']}")
                lines.append(f"      Remediation: {g['remediation']}")
                lines.append(f"      Reference: {g['regulatory_ref']}")
                lines.append("")
        lines.append("")

    return "\n".join(lines)
