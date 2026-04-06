from services.llm import get_llm
import json

from state import ReviewState

def parse_node(state: ReviewState) -> dict:
    llm = get_llm(temperature=0)
    response = llm.invoke(f"""
Analyse this code and return ONLY valid JSON:
{{
  "language": "detected language name",
  "functions": ["list of function/method names"],
  "imports": ["list of imports or dependencies"],
  "line_count": <number of lines>
}}

Code:
{state['code'][:3000]}""")

    try:
        parsed = json.loads(response.content.strip()
                            .replace("```json","").replace("```",""))
        return {
            "language": parsed.get("language", state.get("language","unknown")),
            "functions": parsed.get("functions", []),
            "imports": parsed.get("imports", []),
            "line_count": parsed.get("line_count", len(state["code"].splitlines()))
        }
    except Exception:
        return {
            "language": state.get("language", "unknown"),
            "functions": [],
            "imports": [],
            "line_count": len(state["code"].splitlines())
        }