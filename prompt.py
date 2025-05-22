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
def get_text_from_prompt(response):
    if "candidates" in response:
        text = ""
        for part in response.candidates[0].content.parts:
            text += part.text
        return text
    
    return response.text

text = "Papa Francisco morreu hoje e está em eleição para um novo papa."

prompt1 = [
    (
        f"Analise a mensagem: \"{text}\"\n\n.",
        " Para verificar se é fake news ou não, me diga exatamente separado por linhas, os temas que precisam ser pesquisados, sem gerar dados temporais com base em seus conhecimentos desatualizados. OBS: Não diga mais nada além do que pedi"
    )
]
response_text = None
response_text = get_text_from_prompt(client.models.generate_content(
    model=model_id,
    contents=prompt1,
))
if (response_text.startswith("Sim") or 1==1):
    response_text2= response_text[3:]
    response_text = get_text_from_prompt(
        client.models.generate_content(
            model=model_id,
            contents= f"""Com base na mensagem: "{text}", pesquise detalhadamente os seguintes assuntos: "{response_text2}". Adapte os resultados ao contexto da mensagem, principalmente em relação ao tempo (atualidade), buscando sempre os mais recentes.
                """,
                config=GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            )
        )
    )
else:
    pass
# print(response_text)
response_text = get_text_from_prompt(client.models.generate_content(
    model=model_id,
    contents=f"Analise a mensagem \"{text}\". Analise a veracidade da mensagem com os seguintes resultados de pesquisa: \"{response_text}\". Agora, diga 'É fake news' ou 'Não é fake news' no começo da resposta, depois os motivos. Diga se é fake news apenas se todos os dados condizerem com as pesquisas. OBS: Responda com menos de 1000 caracteres",
))
# for each in response.candidates[0].content.parts:
print(response_text)
# Example response:
# The next total solar eclipse visible in the contiguous United States will be on ...

# To get grounding metadata as web content.
# print(response.candidates[0].grounding_metadata.search_entry_point.rendered_content)