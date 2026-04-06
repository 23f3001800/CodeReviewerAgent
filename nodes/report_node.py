from services.llm import get_llm

def report_node(state: dict) -> dict:
    """Assemble all findings into a final structured markdown report."""

    security = state.get("security_findings", [])
    bugs     = state.get("bug_findings", [])
    quality  = state.get("quality_score", 5)

    # Calculate overall score
    sec_penalty  = sum({"CRITICAL":4,"HIGH":3,"MEDIUM":2,"LOW":1}
                       .get(f.get("severity","LOW"),1) for f in security)
    bug_penalty  = sum({"HIGH":3,"MEDIUM":2,"LOW":1}
                       .get(f.get("severity","LOW"),1) for f in bugs)
    overall      = max(1, min(10, quality - sec_penalty - bug_penalty))

    # Build report sections
    sec_section = ""
    if security:
        sec_section = "## Security Issues\n"
        for f in security:
            line = f"Line {f['line']}" if f.get("line") else "General"
            sec_section += (
                f"\n**[{f['severity']}] {f['issue']}** — {line}\n"
                f"> {f['explanation']}\n\n"
                f"**Fix:** {f['fix']}\n"
            )
    else:
        sec_section = "## Security Issues\n\n✓ No security issues found.\n"

    bug_section = ""
    if bugs:
        bug_section = "## Bugs & Logic Errors\n"
        for f in bugs:
            line = f"Line {f['line']}" if f.get("line") else "General"
            bug_section += (
                f"\n**[{f['severity']}] {f['issue']}** — {line}\n"
                f"> {f['explanation']}\n\n"
                f"**Fix:** {f['fix']}\n"
            )
    else:
        bug_section = "## Bugs & Logic Errors\n\n✓ No bugs found.\n"

    quality_section = (
        f"## Code Quality — {quality}/10\n\n"
        + "\n".join([f"- {n}" for n in state.get("quality_notes", [])])
    )

    report = f"""# Code Review Report

**Language:** {state.get('language','Unknown')} |
**Lines:** {state.get('line_count', '?')} |
**Overall Score: {overall}/10**

---

{sec_section}
---

{bug_section}
---

{quality_section}

---

## Improved Code
```{state.get('language','').lower()}
{state.get('improved_code', 'No improved version generated.')}
```
"""
    return {"final_report": report, "overall_score": overall}