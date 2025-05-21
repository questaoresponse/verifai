import requests
import traceback

from verifai import Verifai

class InternetAnalyzer(Verifai):
    def __init__(self):
        pass
    
    def check_google_api_key(self):
        """
        Script para verificar se a chave da API do Google está funcionando corretamente.
        Execute este script para diagnosticar problemas com a API.
        """
        
        if not self.API_KEY:
            print("ERRO: Chave da API Google não encontrada nas variáveis de ambiente.")
            print("Certifique-se de que GOOGLE_API_KEY está definido no arquivo .env")
            return False
            
        if not self.CSE_ID:
            print("ERRO: ID do Custom Search Engine não encontrado nas variáveis de ambiente.")
            print("Certifique-se de que GOOGLE_CSE_ID está definido no arquivo .env")
            return False
        
        print(f"Verificando chave da API Google: {self.API_KEY[:5]}...{self.API_KEY[-4:] if len(self.API_KEY) > 8 else ''}")
        print(f"Verificando CSE ID: {self.CSE_ID[:5]}...{self.CSE_ID[-4:] if len(self.CSE_ID) > 8 else ''}")
        
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': 'test query',
            'key': self.API_KEY,
            'cx': self.CSE_ID,
            'num': 1
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                print("SUCESSO: A API do Google respondeu corretamente (status 200).")
                data = response.json()
                if 'items' in data:
                    print(f"Encontrados {len(data['items'])} resultados de pesquisa.")
                    print("A chave da API está funcionando corretamente!")
                else:
                    print("AVISO: Nenhum resultado encontrado, mas a API respondeu.")
                return True
            elif response.status_code == 403:
                print("ERRO 403: Acesso Proibido.")
                error_data = response.json()
                print(f"Detalhes do erro: {error_data}")
                print("\nPossíveis causas:")
                print("1. A chave da API é inválida ou está desativada")
                print("2. A chave não tem permissão para acessar a Custom Search API")
                print("3. Você excedeu sua cota diária (verifique o Console do Google Cloud)")
                print("\nVerifique suas credenciais no Google Cloud Console: https://console.cloud.google.com/apis/credentials")
                return False
            elif response.status_code == 400:
                print("ERRO 400: Solicitação inválida.")
                error_data = response.json()
                print(f"Detalhes do erro: {error_data}")
                print("\nVerifique se o ID do Custom Search Engine (cx) está correto.")
                return False
            else:
                print(f"ERRO: Status code inesperado: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"ERRO ao conectar-se à API do Google: {e}")
            return False

    def web_search_api(self, query):
        """Realiza pesquisa usando a API oficial do Google Custom Search."""
        try:
            print(f"[DEBUG] Iniciando pesquisa via API para: '{query}'")
            
            # Verificar se as credenciais existem
            if not self.API_KEY or not self.CSE_ID:
                print("[DEBUG] API_KEY ou CSE_ID não encontrados nas variáveis de ambiente")
                return "Não foi possível realizar a pesquisa: credenciais não configuradas."
                
            search_url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': query,
                'key': self.API_KEY,
                'cx': self.CSE_ID,
                'num': 5,
                'lr': 'lang_pt',
                'safe': 'active'
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            # Verificação mais detalhada do erro
            if response.status_code == 403:
                print(f"[DEBUG] Erro 403 Forbidden: Verifique a chave API ou quota")
                error_details = response.json() if response.text else "Sem detalhes adicionais"
                print(f"[DEBUG] Detalhes do erro: {error_details}")
                return "Não foi possível realizar a pesquisa: erro de autorização na API de busca."
                
            response.raise_for_status()
            search_results = response.json()
            
            extra_info = ""
            if 'items' in search_results:
                for item in search_results['items']:
                    url = item['link']
                    title = item.get('title', 'Sem título')
                    snippet = item.get('snippet', '')
                    extra_info += f"\n\nFONTE: {title} ({url})\n{snippet}\n"
            
            if not extra_info:
                print("[DEBUG] Nenhum resultado retornado pela API de busca.")
                return "Não foi possível encontrar informações confiáveis sobre este assunto."
                
            print(f"[DEBUG] Finalizada pesquisa via API: resultados obtidos.")
            return extra_info
        except requests.exceptions.HTTPError as e:
            error_message = f"[DEBUG] Erro HTTP na pesquisa via API: {e}"
            print(error_message)
            traceback.print_exc()
            return f"Não foi possível realizar a pesquisa: erro no serviço de busca."
        except Exception as e:
            error_message = f"[DEBUG] Erro na pesquisa via API: {e}"
            print(error_message)
            traceback.print_exc()
            return f"Não foi possível realizar a pesquisa: erro interno."
