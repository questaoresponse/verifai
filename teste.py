import os
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# 1. Configure a API do Gemini
genai.configure(api_key=os.getenv("API_KEY_GEMINI"))

# 2. Dados de exemplo
docs = [
    "O Sol é a estrela no centro do sistema solar.",
    "A Lua é o único satélite natural da Terra.",
    "A água ferve a 100 graus Celsius ao nível do mar.",
    "O Brasil tem desigualdade",
    "As pessoas irão morrer em 2040",
    "Universidades dos EUA"
]
titles = ["Sol", "Lua", "Água"]  # títulos opcionais

# 3. Gerar embeddings
model_emb = SentenceTransformer("all-MiniLM-L6-v2")
doc_embeddings = model_emb.encode(docs, normalize_embeddings=True)

# 4. Criar índice FAISS
index = faiss.IndexFlatL2(doc_embeddings.shape[1])
index.add(np.array(doc_embeddings))

# 5. Fazer uma consulta
query = "Maior universidade do Brasil"
query_embedding = model_emb.encode([query], normalize_embeddings=True)
_, top_k = index.search(query_embedding, k=1)

# 6. Recuperar o documento relevante
relevant_doc = docs[top_k[0][0]]

# 7. Gerar resposta com Gemini
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content(f"Responda com base neste texto: \"{relevant_doc}\"\n\nPergunta: {query}")

# 8. Mostrar resultado
print("Pergunta:", query)
print("Documento usado:", relevant_doc)
print("Resposta:", response.text)
