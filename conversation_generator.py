import os
from dotenv import load_dotenv
import openai


def get_response(input_text):
    load_dotenv()
    client = openai.OpenAI(
        base_url=os.getenv('AZURE_OPENAI_API_ENDPOINT'),
        api_key=os.getenv('AZURE_OPENAI_API_KEY')
    )

    system_prompt = "You are a helpful assistant."
    response = client.chat.completions.create(
        model="GPT-4o-mini",
        messages=[
            {"role":"system", "content": system_prompt},
            {"role":"user", "content" : input_text}
        ],
    )
    return response.choices[0].message.content

    