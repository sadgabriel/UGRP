import openai
from config import prompt_path, unstructured_data_path
import os

openai.api_key = os.getenv('openAI_api_key')

with open(prompt_path, 'r') as file:
    prompt = file.read()

response = openai.Completion.create(
    engine="text-davinci-003",  # 사용할 엔진 선택
    prompt=prompt,
    max_tokens=150  # 필요한 토큰 수에 따라 조절
)

# 응답에서 텍스트 추출
result_text = response.choices[0].text.strip()

# 결과를 텍스트 파일로 저장
with open(unstructured_data_path, 'w') as file:
    file.write(result_text)

print(f"Response saved to {unstructured_data_path}")

