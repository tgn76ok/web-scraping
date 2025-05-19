import time
import random
import sys
import signal
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
SLEEP_BETWEEN = 1    # segundos entre ciclos
HEADLESS      = True # ativa modo headless
THRESHOLD     = 8.0  # % acima do 2º colocado para parar

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
    options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2
    })

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

def close_cookie_banner(driver):
    try:
        btn = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fc-button.fc-primary-button"))
        )
        driver.execute_script("arguments[0].click();", btn)
    except:
        pass

def click_read_more(driver):
    try:
        btn = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.widget-btn"))
        )
        driver.execute_script("arguments[0].click();", btn)
    except:
        pass

def vote(driver):
    try:
        print("Aguardando enquete...")
        close_cookie_banner(driver)
        click_read_more(driver)

        checkbox = driver.find_element(By.ID, CANDIDATE_ID)
        driver.execute_script("arguments[0].click();", checkbox)

        vote_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "totalpoll-buttons-vote"))
        )
        driver.execute_script("arguments[0].click();", vote_btn)

        if "obrigado" in driver.page_source.lower():
            print("Voto registrado com sucesso!")
            return True
        else:
            print("Possível falha no voto")
            return False

    except Exception as e:
        print(f"[ERRO] Durante o voto: {e}")
        return False

def get_current_lead(driver):
    """
    Retorna a diferença percentual entre o primeiro e o segundo colocado,
    ordenando todas as porcentagens visíveis na página.
    """
    try:
        WebDriverWait(driver, 5).until(
            EC.visibility_of_all_elements_located(
                (By.CLASS_NAME, "totalpoll-question-choices-item-votes-text")
            )
        )

        elems = driver.find_elements(
            By.CLASS_NAME, "totalpoll-question-choices-item-votes-text"
        )
        percents = []
        for e in elems:
            txt = e.text.replace('%', '').strip()
            try:
                percents.append(float(txt))
            except:
                pass

        if len(percents) < 2:
            return 0.0

        percents.sort()
        return percents[-1] - percents[-2]

    except Exception as e:
        print(f"[ERRO] ao calcular liderança: {e}")
        return 0.0

def worker():
    driver = init_driver()
    while not stop_event.is_set():
        driver.get(SITE_URL)

        ok = vote(driver)
        if not ok:
            print("[WARN] voto falhou, mas checando liderança mesmo assim")

        # Espera breve para o resultado atualizar
        time.sleep(2)

        lead = get_current_lead(driver)
        print(f"[CHECAGEM] Liderança atual: {lead:.2f}%")

        if lead > THRESHOLD:
            print(f"🎉 Liderança > {THRESHOLD}%. Parando todas as threads.")
            stop_event.set()
            break

        clear_data(driver)
        time.sleep(SLEEP_BETWEEN)

    driver.quit()
    print("Driver encerrado.")

def main():
    # Captura CTRL+C
    signal.signal(signal.SIGINT, lambda s, f: stop_event.set())

    print("Iniciando threads de votação...")
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for _ in range(THREADS):
            executor.submit(worker)
        # aguarda até que stop_event seja setado
        stop_event.wait()

    print("Todas as threads encerradas. Saindo.")
    sys.exit(0)

if __name__ == '__main__':
    main()
