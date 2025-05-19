import time
import random
import sys
import signal
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ————— Configurações —————
SITE_URL      = 'https://www.polemicaparaiba.com.br/politica/enquete-polemica-paraiba-em-quem-voce-votaria-para-ser-o-proximo-governador-da-paraiba/'
CANDIDATE_ID  = 'choice-d6a33e0b-f11d-40d8-854b-b318f4cfa492-selector'
THREADS       = 15
PAGE_TIMEOUT  = 10
SLEEP_BETWEEN = 1   # segundos entre ciclos
HEADLESS      = True # ativa modo headless

# ————— Logging centralizado —————
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s [%(threadName)s] %(message)s',
    datefmt='%H:%M:%S'
)

# evento para sinalizar parada
stop_event = threading.Event()

def init_driver():
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--incognito')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.page_load_strategy = 'eager'
    # bloqueia imagens
    options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2
    })
    # user-agent aleatório
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/91.0.4472.114 Safari/537.36"
    ]
    options.add_argument(f'--user-agent={random.choice(user_agents)}')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.set_page_load_timeout(PAGE_TIMEOUT)
    driver.implicitly_wait(3)
    return driver

def clear_data(driver):
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
    logging.debug("Cache e dados limpos")

def close_cookie_banner(driver):
    try:
        btn = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fc-button.fc-primary-button"))
        )
        driver.execute_script("arguments[0].click();", btn)
        logging.info("Banner de cookies fechado")
    except:
        pass

def click_read_more(driver):
    try:
        btn = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.widget-btn"))
        )
        driver.execute_script("arguments[0].click();", btn)
        logging.info("'Leia mais' clicado")
    except:
        pass

def vote(driver):
    try:
        logging.info("Aguardando o carregamento da enquete...")
        close_cookie_banner(driver)
        click_read_more(driver)

        logging.info("Clicando na opção desejada...")
        checkbox = driver.find_element(By.ID, CANDIDATE_ID)
        driver.execute_script("arguments[0].click();", checkbox)

        logging.info("Clicando no botão Votar...")
        vote_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "totalpoll-buttons-vote"))
        )
        driver.execute_script("arguments[0].click();", vote_btn)

        if "obrigado" in driver.page_source.lower():
            logging.info("Voto registrado com sucesso!")
            return True
        else:
            logging.warning("Possível falha no registro do voto")
            return False

    except Exception as e:
        logging.error(f"Erro durante o voto: {e}")
        return False

def worker():
    driver = init_driver()
    while not stop_event.is_set():
        driver.get(SITE_URL)
        vote(driver)
        clear_data(driver)
        time.sleep(SLEEP_BETWEEN)
    driver.quit()
    logging.info("Driver encerrado.")

def main():
    # CTRL+C sinaliza parada
    signal.signal(signal.SIGINT, lambda signum, frame: stop_event.set())

    logging.info("Iniciando threads de votação...")
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for _ in range(THREADS):
            executor.submit(worker)
        stop_event.wait()

    logging.info("Todas as threads encerradas. Saindo.")
    sys.exit(0)

if __name__ == '__main__':
    main()
