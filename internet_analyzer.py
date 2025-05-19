import google.generativeai as generai
import requests
from PIL import Image
from io import BytesIO
import json
import os
from dotenv import load_dotenv

load_dotenv()


API_KEY_GEMINI = os.getenv("API_KEY_GEMINI")
generai.configure(api_key=API_KEY_GEMINI)
model = generai.GenerativeModel("gemini-1.5-pro")

# --- Configuração da SerAPI (Substitua pela sua chave) ---
SERAPI_API_KEY = os.getenv("SERAPI_API_KEY")
SERAPI_ENDPOINT = "https://serpapi.com/search"

# --- Definição da função para busca na web ---
def search_internet(query):
    """Busca informações na internet usando a SerAPI."""
    params = {
        "q": query,
        "api_key": SERAPI_API_KEY,
        "gl": "br",  # Busca no Brasil
        "hl": "pt-BR" # Resultados em português
    }
    response = requests.get(SERAPI_ENDPOINT, params=params)
    response.raise_for_status()  # Lança uma exceção para erros HTTP
    return response.json().get("organic_results", [])

# --- Definição da função para o Function Calling ---
def verificar_noticia_online(legenda, keywords):
    """
    Verifica a veracidade de uma notícia ou informação online.

    Args:
        legenda: A legenda do post do Instagram.
        keywords: Palavras-chave relevantes para a busca.

    Returns:
        Um dicionário contendo o resultado da verificação.
    """
    search_query = f"{legenda} ({' '.join(keywords)}) verificação de fatos"
    search_results = search_internet(search_query)
    contexto = "\n".join([res.get("snippet", "") for res in search_results[:3]]) # Pega os 3 primeiros resultados

    prompt = f"Com base na seguinte legenda do Instagram: '{legenda}' e nos resultados da busca online:\n\n{contexto}\n\nDetermine se o conteúdo do post é provavelmente fake news ou não. Seja direto na sua conclusão e forneça os motivos."
    response = model.generate_content(prompt)
    return {"verificado": True, "analise": response.text}

# --- Definição das funções disponíveis para o Gemini ---
functions = [
    {
        "name": "verificar_noticia_online",
        "description": "Verifica a veracidade de uma notícia ou informação online.",
        "parameters": {
            "type": "object",
            "properties": {
                "legenda": {
                    "type": "string",
                    "description": "A legenda do post do Instagram."
                },
                "keywords": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Palavras-chave relevantes para a busca."
                }
            },
            "required": ["legenda", "keywords"]
        }
    }
]

# --- Função: Enviar para IA com Function Calling ---
def analisar_post_com_internet(legenda, imagem_url):
    response = requests.get(imagem_url)
    imagem = Image.open(BytesIO(response.content))

    prompt = f"Este é um post do Instagram com a seguinte legenda:\n\n{legenda}\n\nAnalise a imagem e a legenda. Se a legenda ou a imagem levantar suspeitas de serem fake news ou informações incorretas, considere usar a função 'verificar_noticia_online' para buscar informações online relevantes. Forneça algumas palavras-chave relevantes para a busca."

    gemini_response = model.generate_content(
        [prompt, imagem],
        generation_config={"temperature": 0.2},
        tools=[{"function_declarations": functions}]
    )

    tool_calls = gemini_response.prompt_feedback.safety_ratings

    if gemini_response.candidates and gemini_response.candidates[0].content.parts:
        print("🧠 Resposta inicial da IA Gemini:\n")
        print(gemini_response.candidates[0].content.parts[0].text)

        if gemini_response.candidates[0].tools_calls:
            print("\n⚙️ Chamada de função detectada:")
            for tool_call in gemini_response.candidates[0].tools_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                if function_name == "verificar_noticia_online":
                    print(f"   - Função: {function_name}")
                    print(f"   - Argumentos: {arguments}")
                    legenda_para_verificar = arguments.get("legenda")
                    keywords_para_verificar = arguments.get("keywords", [])

                    if legenda_para_verificar:
                        print("\n🔎 Verificando informações online...")
                        verification_result = verificar_noticia_online(legenda_para_verificar, keywords_para_verificar)
                        print("\n✅ Resultado da verificação online:\n")
                        print(verification_result['analise'])

    return imagem

# --- Função para baixar informações do post do Instagram (mantida do seu código) ---
def baixar_post_instagram(url):
    try:
        import instaloader
    except ImportError:
        print("Por favor, instale a biblioteca instaloader: pip install instaloader")
        return None, None

    shortcode = url.strip("/").split("/")[-1]
    loader = instaloader.Instaloader(download_pictures=False,
                                     download_video_thumbnails=False,
                                     download_videos=False,
                                     download_comments=False,
                                     save_metadata=False,
                                     post_metadata_txt_pattern='')

    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        legenda = post.caption or "[Sem legenda]"
        url_imagem = post.url  # imagem principal
        return legenda, url_imagem
    except Exception as e:
        print(f"Erro ao baixar informações do post: {e}")
        return None, None

# --- EXECUÇÃO ---
def internet_analyzer(link):
    try:
        legenda, imagem_url = baixar_post_instagram(link)
        if legenda and imagem_url:
            print(legenda)
            return analisar_post_com_internet(legenda, imagem_url)
        else:
            print("❌ Não foi possível obter legenda e/ou URL da imagem.")
    except Exception as e:
        print("❌ Erro geral:", e)