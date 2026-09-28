import ollama
from .prompt import SYSTEM_PROMPT


def generate(context):

    print("TrustLens is analyzing individual ingredients...\n")

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": context
            }
        ],
        options={
            "temperature": 0.1
        }
    )

    return response["message"]["content"]