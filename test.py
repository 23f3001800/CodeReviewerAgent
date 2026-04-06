# test_graph.py
import os
from dotenv import load_dotenv
load_dotenv()

from graph import build_graph

VULNERABLE_CODE = '''
import sqlite3
import subprocess
import pickle

SECRET_KEY = "hardcoded_secret_abc123"

def get_user(username):
    conn = sqlite3.connect("users.db")
    # SQL injection here
    query = f"SELECT * FROM users WHERE username = \'{username}\'"
    result = conn.execute(query).fetchone()
    conn.close()
    return result

def run_command(user_input):
    # Command injection here
    result = subprocess.run(user_input, shell=True, capture_output=True)
    return result.stdout

def load_data(data_bytes):
    # Insecure deserialization
    return pickle.loads(data_bytes)

def calculate(numbers):
    total = 0
    for i in range(len(numbers) + 1):  # off-by-one bug
        total += numbers[i]
    return total
'''

app = build_graph()
result = app.invoke({
    "code": VULNERABLE_CODE,
    "language": "python",
    "filename": "vulnerable.py",
    "chat_history": []
})

print(f"Language:      {result['language']}")
print(f"Functions:     {result['functions']}")
print(f"Overall score: {result['overall_score']}/10")
print(f"Security hits: {len(result['security_findings'])}")
print(f"Bug hits:      {len(result['bug_findings'])}")
print(f"Quality score: {result['quality_score']}/10")
print("\n" + "="*50)
print(result["final_report"])