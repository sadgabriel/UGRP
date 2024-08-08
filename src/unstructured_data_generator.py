from openai import OpenAI
import os
from dotenv import load_dotenv


def unstructured_data_generator(prompt_file_path: str) -> str:

    load_dotenv()
    _api_key = os.getenv("OPENAI_API_KEY")
    if not _api_key:
        raise ValueError("OpenAI API key is not set in environment variables.")

    with open(prompt_file_path, "r") as file:
        prompt = file.read()
        if not prompt:
            raise ValueError(f"The prompt file at {prompt_file_path} is empty.")

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
