# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

def _get_deepseek_client():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        api_key = "YOUR_DEEPSEEK_API_KEY"
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

client = _get_deepseek_client()

def chat_deepseek(prompt):
    response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
            {"role": "system", "content": "You need to engage in deep thinking."},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )

    #print(f"Model is: {response.model}")
    #print(f"Output is: {response.choices[0].message.content}")
    print(response.choices[0].message.reasoning_content)
    return response.choices[0].message.content