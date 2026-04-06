from services.llm import get_llm
import json

SECURITY_PROMPT = """You are a security code reviewer specialising in OWASP Top 10.

Analyse this {language} code for security vulnerabilities ONLY.
Look for: SQL injection, XSS, hardcoded secrets/keys, insecure deserialization,
path traversal, command injection, missing auth checks, insecure direct object refs.

Return ONLY valid JSON array. Empty array if no issues found:
[
  {{
    "line": <line number or null>,
    "severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "issue": "short description",
    "explanation": "why this is dangerous",
    "fix": "how to fix it"
  }}
]

Code:
{code}"""

def security_node(state: ReviewState) -> dict:
    llm = get_llm(temperature=0)
    response = llm.invoke(
        SECURITY_PROMPT.format(
            language=state.get("language", "code"),
            code=state["code"][:4000]
        )
    )
    try:
        findings = json.loads(
            response.content.strip()
            .replace("```json","").replace("```","")
        )
        if not isinstance(findings, list):
            findings = []
    except Exception:
        findings = []

    return {"security_findings": findings}