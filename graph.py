from langgraph.graph import StateGraph, END
from state import ReviewState
from nodes.parse_node import parse_node
from nodes.security_node import security_node

def build_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("parse",    parse_node)
    graph.add_node("security", security_node)

    graph.set_entry_point("parse")
    graph.add_edge("parse",    "security")
    graph.add_edge("security", END)          # expand Day 23

    return graph.compile()

# Quick test
if __name__ == "__main__":
    app = build_graph()
    test_code = """
import sqlite3
def get_user(username):
    conn = sqlite3.connect('users.db')
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return conn.execute(query).fetchone()
"""
    result = app.invoke({
        "code": test_code,
        "language": "python",
        "filename": "test.py",
        "chat_history": []
    })
    print("Language:", result["language"])
    print("Functions:", result["functions"])
    print("\nSecurity findings:")
    for f in result["security_findings"]:
        print(f"  [{f['severity']}] Line {f.get('line','?')}: {f['issue']}")




# from langgraph.graph import StateGraph, END
# from state import ReviewState
# from nodes.parse_node    import parse_node
# from nodes.security_node import security_node
# from nodes.bugs_node     import bugs_node
# from nodes.quality_node  import quality_node
# from nodes.improve_node  import improve_node
# from nodes.report_node   import report_node

# def build_graph():
#     graph = StateGraph(ReviewState)

#     graph.add_node("parse",    parse_node)
#     graph.add_node("security", security_node)
#     graph.add_node("bugs",     bugs_node)
#     graph.add_node("quality",  quality_node)
#     graph.add_node("improve",  improve_node)
#     graph.add_node("report",   report_node)

#     # Parse first — all others need language + structure
#     graph.set_entry_point("parse")

#     # Fan-out: security, bugs, quality run in parallel after parse
#     graph.add_edge("parse", "security")
#     graph.add_edge("parse", "bugs")
#     graph.add_edge("parse", "quality")

#     # Fan-in: improve waits for ALL THREE to complete
#     graph.add_edge("security", "improve")
#     graph.add_edge("bugs",     "improve")
#     graph.add_edge("quality",  "improve")

#     # Report assembles everything
#     graph.add_edge("improve", "report")
#     graph.add_edge("report",  END)

#     return graph.compile()