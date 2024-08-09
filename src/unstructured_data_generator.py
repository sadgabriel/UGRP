from openai import OpenAI
import os
from dotenv import load_dotenv


def unstructured_data_generator(prompt: str) -> str:

    load_dotenv()
    _api_key = os.getenv("OPENAI_API_KEY")
    if not _api_key:
        raise ValueError("OpenAI API key is not set in environment variables.")

    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "",
            },
            {
                "role": "user",
                "content": f"{prompt}",
            },
        ],
    )

    return completion.choices[0].message.content
