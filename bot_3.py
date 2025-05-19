import requests
import uuid
import time
from fake_useragent import UserAgent

# Configurações - PREENCHA ESTES VALORES ANTES DE USAR
URL_DA_ENQUETE = "https://www.polemicaparaiba.com.br/politica/enquete-polemica-paraiba-em-quem-voce-votaria-para-ser-o-proximo-governador-da-paraiba/"  # URL da página de votação
NUMERO_DE_VOTOS = 1000                         # Quantidade de votos a serem enviados
DELAY_ENTRE_VOTOS = 0                        # Delay em segundos entre votos

# Configurações fixas (ajuste se necessário)
POLL_ID = "1111618"
CHOICE_UUID = "d6a33e0b-f11d-40d8-854b-b318f4cfa492"

# Inicializa UserAgent para headers aleatórios
ua = UserAgent()

for i in range(NUMERO_DE_VOTOS):
    try:
        # Cria nova sessão
        session = requests.Session()
        
        # Gera cookies únicos
        session_id = str(uuid.uuid4()).replace("-", "")
        cookie_value = f"{session_id[:8]}-{session_id[8:12]}-{session_id[12:16]}-{session_id[16:20]}-{session_id[20:]}"
        
        cookies = {
            "tp_469f4fb05e034c5f02005fcefe4a590c": cookie_value,
            "tp_888528ee1239aabb66bc30459c8a90eee": "1"
        }
        
        # Configura headers aleatórios
        headers = {
            "User-Agent": ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": URL_DA_ENQUETE,
            "Origin": URL_DA_ENQUETE.split('/')[0] + "//" + URL_DA_ENQUETE.split('/')[2],
            "Connection": "keep-alive"
        }
        
        # Gera boundary único
        boundary = f"boundary{uuid.uuid4().hex}"
        
        # Monta o corpo da requisição
        data = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="totalpoll[choices][9368332c-8ee9-447c-9009-3bab6e2e6107][]"\r\n\r\n'
            f'{CHOICE_UUID}\r\n'
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="totalpoll[screen]"\r\n\r\n'
            f'vote\r\n'
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="totalpoll[pollId]"\r\n\r\n'
            f'{POLL_ID}\r\n'
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="totalpoll[action]"\r\n\r\n'
            f'vote\r\n'
            f'--{boundary}--\r\n'
        )
        
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        
        # Envia o voto
        response = session.post(
            URL_DA_ENQUETE,
            headers=headers,
            cookies=cookies,
            data=data.encode('utf-8'),
            timeout=10
        )
        
        print(f"Voto {i+1}/{NUMERO_DE_VOTOS} enviado:")
        print(f"Status: {response.status_code}")
        print(f"Cookies: {cookies}")
        print("-" * 50)
        
        time.sleep(DELAY_ENTRE_VOTOS)
        
    except Exception as e:
        print(f"Erro no voto {i+1}: {str(e)}")
        continue

print("Processo de votação concluído!")