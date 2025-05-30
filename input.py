# import instaloader
# import os
# import time
# from google import genai
# from dotenv import load_dotenv

# # Carrega variáveis de ambiente
# load_dotenv()

# API_KEY_GEMINI = os.getenv("API_KEY_GEMINI")

# client = genai.Client(api_key=API_KEY_GEMINI)


# filename = "verifica_ai_temp/v_17908475286035819.mp4"
# file = client.files.upload(file = filename)

# state = genai.types.FileState.PROCESSING
# while state == genai.types.FileState.PROCESSING:
#     status = client.files.get(name = file.name).state
#     time.sleep(1)

# response = client.models.generate_content(
#     model="gemini-2.0-flash", contents=["Faça a análise desse video. Primeiramente, me diga se é fake news ou não diretamente. Depois diga os motivos. OBS: Responda com no máximo 1000 caracteres.", file]
# )
# client.files.delete(name = file.name)
# print(response.text)

from google import genai
import os
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

API_KEY_GEMINI = os.getenv("API_KEY_GEMINI")

client = genai.Client(api_key=API_KEY_GEMINI)

model_id = "gemini-2.0-flash"

google_search_tool = Tool(
    google_search = GoogleSearch()
)

response = client.models.generate_content(
    model=model_id,
    contents="When is the next total solar eclipse in the United States?",
    config=GenerateContentConfig(
        tools=[google_search_tool],
        response_modalities=["TEXT"],
    )
)

# for each in response.candidates[0].content.parts:
for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
    print(chunk.web.uri)
# Example response:
# The next total solar eclipse visible in the contiguous United States will be on ...

# To get grounding metadata as web content.
# print(response.candidates[0].grounding_metadata.search_entry_point.rendered_content)