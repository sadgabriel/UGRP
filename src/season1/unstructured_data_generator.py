import os

from openai import OpenAI
from dotenv import load_dotenv


def unstructured_data_generate(system: str, param: str) -> str:

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
                "content": f"{system}",
            },
            {
                "role": "user",
                "content": f"{param}",
            },
        ],
        max_tokens=16384,
    )

    return completion.choices[0].message.content
