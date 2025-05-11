# pip install openai
from openai import OpenAI

client = OpenAI(
    api_key="525c607104d8891a998419b0d2ad22e0f2f26a7f",
    base_url="https://api-xa0fv6o8a9m1q9hd.aistudio-app.com/v1"
)

completion = client.chat.completions.create(
    model="deepseek-r1:8b",
    temperature=0.6,
    messages=[
        {"role": "user", "content": "请根据病情给病人给出合适的药物和计量,并给出合理的用药建议"}
    ],
    stream=True
)

for chunk in completion:
    if hasattr(chunk.choices[0].delta, "reasoning_content") and chunk.choices[0].delta.reasoning_content:
        print(chunk.choices[0].delta.reasoning_content, end="", flush=True)
    else:
        print(chunk.choices[0].delta.content, end="", flush=True)