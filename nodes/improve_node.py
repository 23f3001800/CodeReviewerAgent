from services.llm import get_llm

IMPROVE_PROMPT = """You are a senior {language} engineer. Rewrite this code with all issues fixed.

Issues to fix:
Security: {security}
Bugs: {bugs}
Quality: {quality}

Rules:
- Fix every identified issue
- Add inline comments explaining each significant change
- Keep the same overall structure and function signatures
- Do not add features that weren't requested

Original code:
{code}

Return ONLY the improved code. No explanation outside the code."""

def improve_node(state: dict) -> dict:
    llm = get_llm(temperature=0.1)

    # Summarise findings for the prompt
    sec_summary = "; ".join([
        f"{f['severity']}: {f['issue']}"
        for f in state.get("security_findings", [])[:5]
    ]) or "None found"

    bug_summary = "; ".join([
        f"{f['severity']}: {f['issue']}"
        for f in state.get("bug_findings", [])[:5]
    ]) or "None found"

    quality_summary = "; ".join(
        state.get("quality_notes", [])[:3]
    ) or "None found"

    response = llm.invoke(
        IMPROVE_PROMPT.format(
            language=state.get("language", "code"),
            security=sec_summary,
            bugs=bug_summary,
            quality=quality_summary,
            code=state["code"][:4000]
        )
    )
    improved = response.content.strip()
    # Strip markdown code fences if present
    if improved.startswith("```"):
        lines = improved.split("\n")
        improved = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    return {"improved_code": improved}