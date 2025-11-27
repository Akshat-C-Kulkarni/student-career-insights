# scripts/test_llm.py
import os
import sys
sys.path.append("app")

from llm import call_openrouter_chat

messages = [
    {"role": "system", "content": "You are a helpful assistant that provides short, structured career advice."},
    {"role": "user", "content": "Give me 3 short project ideas for a Cloud Engineer beginner."}
]

resp = call_openrouter_chat(messages)
print(resp)
if resp.get("ok"):
    print("\n== ASSISTANT ===\n", resp["content"])
else:
    print("\n== ERROR ===\n", resp)
