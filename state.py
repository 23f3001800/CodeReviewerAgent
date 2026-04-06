from typing import TypedDict, List, Optional



class ReviewState(TypedDict):
    # Input
    code: str
    language: str          # auto-detected or user-provided
    filename: str

    # Parse output
    functions: List[str]   # extracted function names
    imports: List[str]     # detected imports/dependencies
    line_count: int

    # Review outputs (populated in parallel)
    security_findings: List[dict]   # [{line, severity, issue, fix}]
    bug_findings: List[dict]
    quality_score: int              # 1–10
    quality_notes: List[str]

    # Synthesis
    improved_code: str
    final_report: str
    overall_score: int              # 1–10

    # Conversation
    chat_history: List[dict]
    error: Optional[str]

    