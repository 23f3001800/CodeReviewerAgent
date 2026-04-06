from services.llm import get_llm
import json

BUGS_PROMPT = """You are an expert {language} developer doing a code review.

Find bugs, logic errors, and edge cases ONLY — not style issues, not security.
Look for: null/undefined handling, off-by-one errors, unhandled exceptions,
incorrect conditionals, race conditions, resource leaks, wrong return types.

Return ONLY a valid JSON array. Empty array if no bugs found:
[
  {{
    "line": <line number or null>,
    "severity": "HIGH|MEDIUM|LOW",
    "issue": "short description of the bug",
    "explanation": "why this causes a problem",
    "fix": "concrete fix with example code if helpful"
  }}
]

Code:
{code}"""

def bugs_node(state: dict) -> dict:
    llm      = get_llm(temperature=0)
    response = llm.invoke(
        BUGS_PROMPT.format(
            language=state.get("language", "code"),
            code=state["code"][:4000]
        )
    )
    try:
        findings = json.loads(
            response.content.strip()
            .replace("```json","").replace("```","").strip()
        )
        if not isinstance(findings, list):
            findings = []
    except Exception:
        findings = []
    return {"bug_findings": findings}