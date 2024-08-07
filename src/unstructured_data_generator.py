import openai
from config import prompt_path
import os


def unstructured_data_generator() -> str:
    try:
        openai.api_key = os.getenv("openAI_api_key")
        if not openai.api_key:
            raise ValueError("OpenAI API key is not set in environment variables.")

        with open(prompt_path, "r") as file:
            prompt = file.read()
            if not prompt:
                raise ValueError(f"The prompt file at {prompt_path} is empty.")

        response = openai.Completion.create(
            engine="text-davinci-003",  # Use the selected engine
            prompt=prompt,
            max_tokens=150,  # Adjust according to required tokens
        )

        # Extract text from the response
        result = response.choices[0].text.strip()
        print("Success: The data was generated successfully.")
        return result

    except FileNotFoundError:
        return f"Error: The prompt file at {prompt_path} was not found."
    except ValueError as ve:
        return f"Error: {ve}"
    except openai.error.OpenAIError as oe:
        return f"OpenAI API error: {oe}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
