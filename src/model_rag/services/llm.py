import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_MODEL = "openai/gpt-oss-20b" # apne working project wala model naam yahan likhein

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate(prompt: str) -> str:
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return completion.choices[0].message.content


if __name__ == "__main__":
    print(generate("Tell me some good points for using free groq api key and list some models and one linear descriotion for which model is used for which purpose ."))
