import streamlit as st
from dotenv import load_dotenv
import os, requests, re

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"]  = "true"
os.environ["LANGCHAIN_PROJECT"]     = "code-reviewer"

from graph import build_graph

st.set_page_config(
    page_title="CodeSense — AI Code Reviewer",
    page_icon="🔍",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
.severity-critical {
    background:#FCEBEB;color:#A32D2D;
    padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600
}
.severity-high {
    background:#FAEEDA;color:#854F0B;
    padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600
}
.severity-medium {
    background:#E6F1FB;color:#185FA5;
    padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600
}
.severity-low {
    background:#EAF3DE;color:#3B6D11;
    padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600
}
.score-badge {
    font-size:48px;font-weight:700;text-align:center;
    padding:16px;border-radius:12px;margin-bottom:8px
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
for key, default in [
    ("review_result", None),
    ("chat_history",  []),
    ("code_input",    ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Helpers ───────────────────────────────────────────────────
def score_color(score: int) -> str:
    if score >= 8: return "#1D9E75"
    if score >= 5: return "#BA7517"
    return "#A32D2D"

def severity_badge(severity: str) -> str:
    cls = f"severity-{severity.lower()}"
    return f'<span class="{cls}">{severity}</span>'

def fetch_github_pr(pr_url: str) -> str:
    """Fetch changed files from a GitHub PR URL."""
    # Parse owner/repo/pr_number from URL
    pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match   = re.search(pattern, pr_url)
    if not match:
        return ""
    owner, repo, pr_num = match.groups()

    headers = {}
    gh_token = os.getenv("GITHUB_TOKEN", "")
    if gh_token:
        headers["Authorization"] = f"token {gh_token}"

    # Get PR files via GitHub API
    api_url  = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}/files"
    response = requests.get(api_url, headers=headers, timeout=10)
    if response.status_code != 200:
        return ""

    files     = response.json()
    all_code  = []
    for f in files[:5]:   # review up to 5 changed files
        filename = f.get("filename","")
        patch    = f.get("patch","")
        if patch:
            all_code.append(f"# File: {filename}\n{patch}")
    return "\n\n".join(all_code)

def run_review(code: str, language: str, filename: str):
    """Run the LangGraph review pipeline."""
    graph  = build_graph()
    result = graph.invoke({
        "code":         code,
        "language":     language,
        "filename":     filename,
        "chat_history": []
    })
    return result

# ── Header ────────────────────────────────────────────────────
st.title("🔍 CodeSense")
st.caption("AI-powered code reviewer — bugs, security, quality, improvements")

# ── Sidebar: input options ─────────────────────────────────────
with st.sidebar:
    st.header("Input")
    input_mode = st.radio(
        "Source",
        ["Paste code", "GitHub PR URL"],
        horizontal=True
    )

    language = st.selectbox(
        "Language",
        ["Auto-detect", "Python", "JavaScript", "TypeScript",
         "Java", "Go", "Rust", "C++", "SQL"]
    )

    if input_mode == "GitHub PR URL":
        pr_url = st.text_input(
            "PR URL",
            placeholder="https://github.com/owner/repo/pull/123"
        )
        if st.button("Fetch PR diff", type="secondary"):
            with st.spinner("Fetching PR diff from GitHub..."):
                code = fetch_github_pr(pr_url)
            if code:
                st.session_state.code_input = code
                st.success("PR diff fetched!")
            else:
                st.error("Could not fetch PR. Check URL or add GITHUB_TOKEN to .env for private repos.")

    st.markdown("---")
    st.caption("Add `GITHUB_TOKEN=...` to `.env` to review private repos.")

# ── Main area: two columns ────────────────────────────────────
left, right = st.columns([1, 1], gap="medium")

with left:
    st.subheader("Your code")
    code_input = st.text_area(
        label="code",
        value=st.session_state.code_input,
        height=400,
        placeholder="Paste your code here...",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        review_btn = st.button(
            "Review code →",
            type="primary",
            disabled=not code_input.strip(),
            use_container_width=True
        )
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.review_result = None
            st.session_state.chat_history  = []
            st.session_state.code_input    = ""
            st.rerun()

    if review_btn and code_input.strip():
        lang = "" if language == "Auto-detect" else language
        with st.spinner("Reviewing your code... (parse → security + bugs + quality → improve → report)"):
            try:
                result = run_review(
                    code=code_input,
                    language=lang,
                    filename="review.py"
                )
                st.session_state.review_result = result
                st.session_state.chat_history  = []
            except Exception as e:
                st.error(f"Review failed: {e}")

with right:
    if st.session_state.review_result is None:
        st.info("Paste your code on the left and click **Review code →** to start.")
    else:
        result = st.session_state.review_result

        # ── Score banner ─────────────────────────────────────
        score = result.get("overall_score", 5)
        color = score_color(score)
        st.markdown(
            f'<div class="score-badge" style="background:{color}22;color:{color}">'
            f'{score}/10</div>',
            unsafe_allow_html=True
        )
        cols = st.columns(3)
        cols[0].metric("Security issues", len(result.get("security_findings",[])))
        cols[1].metric("Bugs found",      len(result.get("bug_findings",[])))
        cols[2].metric("Quality score",   f"{result.get('quality_score',0)}/10")

        # ── Tabs: findings + improved code ───────────────────
        tab1, tab2, tab3, tab4 = st.tabs([
            "Security", "Bugs", "Quality", "Improved code"
        ])

        with tab1:
            findings = result.get("security_findings", [])
            if not findings:
                st.success("No security issues found.")
            for f in findings:
                with st.expander(
                    f"[{f.get('severity','?')}] {f.get('issue','Unknown')} "
                    f"— Line {f.get('line','?')}"
                ):
                    st.markdown(f"**Why it's dangerous:** {f.get('explanation','')}")
                    st.code(f.get('fix',''), language="python")

        with tab2:
            findings = result.get("bug_findings", [])
            if not findings:
                st.success("No bugs found.")
            for f in findings:
                with st.expander(
                    f"[{f.get('severity','?')}] {f.get('issue','Unknown')} "
                    f"— Line {f.get('line','?')}"
                ):
                    st.markdown(f"**What goes wrong:** {f.get('explanation','')}")
                    st.code(f.get('fix',''), language="python")

        with tab3:
            score = result.get("quality_score", 5)
            st.progress(score / 10, text=f"Quality: {score}/10")
            for note in result.get("quality_notes", []):
                st.markdown(f"- {note}")

        with tab4:
            improved = result.get("improved_code","")
            if improved:
                lang_key = result.get("language","python").lower()
                st.code(improved, language=lang_key)
                st.download_button(
                    "⬇ Download improved code",
                    data=improved,
                    file_name=f"improved_{result.get('filename','code.py')}",
                    mime="text/plain"
                )
            else:
                st.info("No improved version generated.")

# ── Conversational follow-up ──────────────────────────────────
if st.session_state.review_result:
    st.markdown("---")
    st.subheader("Ask about your code")
    st.caption("Ask follow-up questions about the review findings.")

    # Render chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Why is line 12 a security risk? How do I fix the off-by-one?")
    if question:
        st.session_state.chat_history.append({
            "role": "user", "content": question
        })
        with st.chat_message("user"):
            st.markdown(question)

        # Build context from review result
        result  = st.session_state.review_result
        context = f"""
Code reviewed ({result.get('language','unknown')}):
{result.get('code','')}

Security findings: {result.get('security_findings',[])}
Bug findings: {result.get('bug_findings',[])}
Quality notes: {result.get('quality_notes',[])}
Improved code: {result.get('improved_code','')}
"""
        from services.llm import get_llm
        llm = get_llm(temperature=0.2)

        history_text = "\n".join([
            f"{m['role'].upper()}: {m['content']}"
            for m in st.session_state.chat_history[:-1]
        ])

        prompt = f"""You are a code review assistant. Answer based ONLY on the review below.
Be specific — reference line numbers and actual code when relevant.

Review context:
{context}

Conversation so far:
{history_text}

User question: {question}
Answer:"""

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = llm.invoke(prompt).content
            st.markdown(answer)

        st.session_state.chat_history.append({
            "role": "assistant", "content": answer
        })