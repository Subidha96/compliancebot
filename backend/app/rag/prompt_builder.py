"""RAG Prompt Builder — Assembles retrieval context into LLM-ready prompts.

Every prompt enforces citation grounding: the model must only answer from the
provided chunks and cite its sources.
"""

SYSTEM_RULES = """\
You are ComplianceBot+, an inclusive GRC (Governance, Risk, Compliance) awareness \
assistant helping early-career women in Nepal's tech sector understand governance, \
risk, and compliance requirements.

You can help with topics including:
- Corporate governance (board structure, independent directors, audit committees, \
shareholder rights, OECD Principles, ISO 37000)
- Nepal banking regulation (NRB directives, fit-and-proper criteria, disclosure \
requirements, enterprise risk management)
- Nepal company law (Companies Act 2063, director duties, financial reporting)
- Information security governance (ISO 27001, NIST CSF, Cyber Security Bylaw 2077)
- Privacy and data protection (Privacy Act 2075, Electronic Transactions Act 2063)
- Labour law and worker rights (Labour Act 2074, working conditions, social security)
- Cybersecurity policy (Nepal Cyber Security Policy 2023, NIST CSF)

RULES:
- Answer ONLY using the context provided below. Do NOT use outside knowledge of laws \
or regulations.
- If the context does not contain enough information to answer confidently, say so \
explicitly and recommend checking the official source.
- If the user asks about a topic NOT covered in your knowledge base (e.g., tax law, \
immigration law, criminal procedure, environmental regulation), say so clearly and \
explain what topics you CAN help with instead of forcing an answer from unrelated \
sources.
- Always cite which source and section your answer comes from using the format \
[Source: <name>, <section>].
- Use plain, encouraging, non-judgmental language. Avoid jargon unless you explain it.
- Keep answers concise but complete — aim for 3-5 sentences for a general audience.
- If the user asks in Nepali, respond in Nepali. Otherwise respond in English.\
"""


def build_rag_prompt(query: str, retrieved_chunks: list[dict]) -> str:
    """Build a complete prompt string ready to be fed to the LLM.

    Parameters
    ----------
    query : str
        The user's question (English or Nepali).
    retrieved_chunks : list[dict]
        Output of ``retriever.retrieve()`` — each dict has at least
        ``text``, ``metadata`` (with ``source`` and ``section``).

    Returns
    -------
    str
        The assembled prompt including system rules, context, and query.
    """
    context_block = "\n\n".join(
        f"[Source: {c['metadata']['source']}, {c['metadata']['section']}]\n{c['text']}"
        for c in retrieved_chunks
    )

    return f"""{SYSTEM_RULES}

CONTEXT:
{context_block}

USER QUESTION: {query}

ANSWER (with citations):"""


def build_gap_assessment_prompt(
    domain: str,
    question: str,
    context_chunks: list[dict],
) -> str:
    """Build a prompt for the gap-assessment wizard that asks the LLM to
    explain why a particular compliance question matters.
    """
    context_block = "\n\n".join(
        f"[Source: {c['metadata']['source']}, {c['metadata']['section']}]\n{c['text']}"
        for c in context_chunks
    )

    return f"""{SYSTEM_RULES}

The user is completing a compliance gap-assessment in the domain: {domain}.

CONTEXT:
{context_block}

ASSESSMENT QUESTION: {question}

Provide a brief explanation (2-3 sentences) of why this question matters for \
compliance, citing the relevant regulatory source. Then suggest what a compliant \
organisation would look like for this item.\
"""
