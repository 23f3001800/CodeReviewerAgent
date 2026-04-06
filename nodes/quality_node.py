from services.llm import get_llm
import json

QUALITY_PROMPT = """You are a senior {language} engineer reviewing code quality.

Evaluate ONLY: readability, naming conventions, function length, complexity,
code duplication, missing docstrings/comments, test coverage gaps.
Do NOT flag security or bugs — those are reviewed separately.

Return ONLY valid JSON:
{{
  "score": <integer 1-10>,
  "summary": "one sentence overall assessment",
  "notes": [
    "specific actionable improvement 1",
    "specific actionable improvement 2",
    "specific actionable improvement 3"
  ],
  "strengths": ["what is already good"]
}}

Code:
{code}"""

def quality_node(state: dict) -> dict:
    llm      = get_llm(temperature=0)
    response = llm.invoke(
        QUALITY_PROMPT.format(
            language=state.get("language", "code"),
            code=state["code"][:4000]
        )
    )
    try:
        result = json.loads(
            response.content.strip()
            .replace("```json","").replace("```","").strip()
        )
        return {
            "quality_score": int(result.get("score", 5)),
            "quality_notes": result.get("notes", []) + result.get("strengths", []),
            "quality_summary": result.get("summary", "")
        }
    except Exception:
        return {
            "quality_score": 5,
            "quality_notes": [],
            "quality_summary": "Quality analysis unavailable"
        }