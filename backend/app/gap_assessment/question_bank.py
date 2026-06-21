"""Gap Assessment Question Bank — 25 questions across 5 compliance domains.

Questions are drawn from Nepal's regulatory framework and aligned with
ISO 27001:2022 Annex A and NIST CSF 2.0 categories.
"""
from dataclasses import dataclass


@dataclass
class Question:
    """A single gap-assessment question."""
    id: str
    domain: str
    domain_code: str
    text: str
    options: list[str]
    regulatory_ref: str
    weight: float = 1.0  # relative importance within domain


# ---------------------------------------------------------------------------
# Domain 1: Incident Response (IR) — 5 questions
# ---------------------------------------------------------------------------

IR_QUESTIONS = [
    Question(
        id="IR-01",
        domain="Incident Response",
        domain_code="IR",
        text="Does your organisation have a documented incident response plan (IRP) that defines roles, responsibilities, and procedures for handling security incidents?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.5.24; Nepal Cyber Security Policy 2023 §4",
    ),
    Question(
        id="IR-02",
        domain="Incident Response",
        domain_code="IR",
        text="Has your organisation established a dedicated Incident Response Team (IRT) with a designated team lead?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.5.24; Cyber Security Bylaw 2077 §7",
    ),
    Question(
        id="IR-03",
        domain="Incident Response",
        domain_code="IR",
        text="Do you have a documented process for notifying the Nepal Telecommunications Authority (NTA) of security incidents within 24 hours?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="Cyber Security Bylaw 2077 §8; NIST CSF RS.CO",
    ),
    Question(
        id="IR-04",
        domain="Incident Response",
        domain_code="IR",
        text="Is there a regular schedule (at least annually) for testing and updating the incident response plan through tabletop exercises or simulations?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.5.27; NIST CSF RS.RP",
    ),
    Question(
        id="IR-05",
        domain="Incident Response",
        domain_code="IR",
        text="Does your organisation maintain an evidence preservation and forensic investigation capability for security incidents?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="NIST SP 800-61; ISO 27001 Annex A.5.25",
    ),
]

# ---------------------------------------------------------------------------
# Domain 2: Data Protection (DP) — 5 questions
# ---------------------------------------------------------------------------

DP_QUESTIONS = [
    Question(
        id="DP-01",
        domain="Data Protection",
        domain_code="DP",
        text="Does your organisation collect explicit, informed consent before processing personal data?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="Individual Privacy Act 2075 §5-6; Data Act 2079",
    ),
    Question(
        id="DP-02",
        domain="Data Protection",
        domain_code="DP",
        text="Do you have a documented data retention policy that specifies retention periods for each data category?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="Individual Privacy Act 2075 §8; ISO 27001 Annex A.8.10",
    ),
    Question(
        id="DP-03",
        domain="Data Protection",
        domain_code="DP",
        text="Can individuals exercise their right to access, correct, or delete their personal data held by your organisation?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="Individual Privacy Act 2075 §10-11",
    ),
    Question(
        id="DP-04",
        domain="Data Protection",
        domain_code="DP",
        text="Do you have a Data Protection Officer (DPO) or designated person responsible for privacy compliance?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="Individual Privacy Act 2075; ISO 27001 Annex A.5.2",
    ),
    Question(
        id="DP-05",
        domain="Data Protection",
        domain_code="DP",
        text="Do you have a documented process for notifying affected individuals and the Privacy Commission within 72 hours of a personal data breach?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="Individual Privacy Act 2075 §42; Proposed Data Protection Act §23-25",
    ),
]

# ---------------------------------------------------------------------------
# Domain 3: Access Controls (AC) — 5 questions
# ---------------------------------------------------------------------------

AC_QUESTIONS = [
    Question(
        id="AC-01",
        domain="Access Controls",
        domain_code="AC",
        text="Does your organisation enforce the principle of least privilege — granting users only the minimum access needed for their role?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.9.2; NIST CSF PR.AC",
    ),
    Question(
        id="AC-02",
        domain="Access Controls",
        domain_code="AC",
        text="Is multi-factor authentication (MFA) implemented for all critical systems and administrative accounts?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="Nepal Cyber Security Policy 2023 §3.4; ISO 27001 Annex A.8.5",
    ),
    Question(
        id="AC-03",
        domain="Access Controls",
        domain_code="AC",
        text="Do you conduct regular access reviews (at least quarterly) to revoke unnecessary or excessive privileges?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.9.2; NIST CSF PR.AC",
    ),
    Question(
        id="AC-04",
        domain="Access Controls",
        domain_code="AC",
        text="Is there a formal user registration and de-registration process for granting and revoking system access?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.9.1-9.2; NIST CSF PR.AC-1",
    ),
    Question(
        id="AC-05",
        domain="Access Controls",
        domain_code="AC",
        text="Do you have privileged access management (PAM) controls for administrator accounts, including audit logging?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.8.2; NIST CSF PR.AC-4",
    ),
]

# ---------------------------------------------------------------------------
# Domain 4: Security Awareness Training (SA) — 5 questions
# ---------------------------------------------------------------------------

SA_QUESTIONS = [
    Question(
        id="SA-01",
        domain="Security Awareness",
        domain_code="SA",
        text="Does your organisation provide mandatory security awareness training to all employees upon onboarding?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.6.3; NIST CSF PR.AT",
    ),
    Question(
        id="SA-02",
        domain="Security Awareness",
        domain_code="SA",
        text="Is there an annual refresher training programme covering current threats (phishing, social engineering, data handling)?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="Cyber Security Bylaw 2077 §5; ISO 27001 Annex A.6.3",
    ),
    Question(
        id="SA-03",
        domain="Security Awareness",
        domain_code="SA",
        text="Do you run simulated phishing campaigns to test and measure employee awareness?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="NIST CSF PR.AT; ISO 27001 Annex A.6.3",
    ),
    Question(
        id="SA-04",
        domain="Security Awareness",
        domain_code="SA",
        text="Is security awareness training role-specific (e.g., developers get secure coding, executives get governance)?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.6.3; NIST CSF PR.AT-2",
    ),
    Question(
        id="SA-05",
        domain="Security Awareness",
        domain_code="SA",
        text="Does your organisation track and document training completion rates for audit evidence?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.6.3; Cyber Security Bylaw 2077",
    ),
]

# ---------------------------------------------------------------------------
# Domain 5: Third-Party Risk (TPR) — 5 questions
# ---------------------------------------------------------------------------

TPR_QUESTIONS = [
    Question(
        id="TPR-01",
        domain="Third-Party Risk",
        domain_code="TPR",
        text="Does your organisation maintain an inventory of all third-party suppliers and their access to your systems/data?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.5.19; NIST CSF ID.SC",
    ),
    Question(
        id="TPR-02",
        domain="Third-Party Risk",
        domain_code="TPR",
        text="Do you conduct security risk assessments before onboarding new third-party vendors?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.5.20; NIST CSF ID.SC-2",
    ),
    Question(
        id="TPR-03",
        domain="Third-Party Risk",
        domain_code="TPR",
        text="Are contractual security requirements (data protection, incident reporting, audit rights) included in all vendor agreements?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.5.21; NIST CSF ID.SC-3",
    ),
    Question(
        id="TPR-04",
        domain="Third-Party Risk",
        domain_code="TPR",
        text="Do you periodically review third-party compliance status and security posture?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.5.22; NIST CSF ID.SC-4",
    ),
    Question(
        id="TPR-05",
        domain="Third-Party Risk",
        domain_code="TPR",
        text="Is there a documented process for terminating third-party access and reclaiming assets when a vendor relationship ends?",
        options=["Yes", "Partially", "No"],
        regulatory_ref="ISO 27001 Annex A.5.23; NIST CSF ID.SC-5",
    ),
]


# ---------------------------------------------------------------------------
# All questions combined
# ---------------------------------------------------------------------------

ALL_QUESTIONS: list[Question] = (
    IR_QUESTIONS
    + DP_QUESTIONS
    + AC_QUESTIONS
    + SA_QUESTIONS
    + TPR_QUESTIONS
)

DOMAINS = {
    "IR": "Incident Response",
    "DP": "Data Protection",
    "AC": "Access Controls",
    "SA": "Security Awareness",
    "TPR": "Third-Party Risk",
}

DOMAIN_QUESTIONS = {
    "IR": IR_QUESTIONS,
    "DP": DP_QUESTIONS,
    "AC": AC_QUESTIONS,
    "SA": SA_QUESTIONS,
    "TPR": TPR_QUESTIONS,
}
