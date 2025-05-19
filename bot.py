import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import stem.process
from stem import Signal
from stem.control import Controller
import random
import threading
import time
import sys


# Configuração do Tor
TOR_PORT = 9050
CONTROL_PORT = 9051
TOR_PASSWORD = "123"  # Altere para a senha que configurou no Tor
SITE_URL = 'https://www.polemicaparaiba.com.br/politica/enquete-polemica-paraiba-em-quem-voce-votaria-para-ser-o-proximo-governador-da-paraiba/'

def get_new_tor_ip():
    """Solicita um novo circuito Tor (novo IP)"""
    with Controller.from_port(port=CONTROL_PORT) as controller:
        controller.authenticate(password=TOR_PASSWORD)
        controller.signal(Signal.NEWNYM)
        time.sleep(controller.get_newnym_wait())  # Espera o tempo necessário para evitar rate limiting

def start_tor():
    """Inicia o processo Tor se não estiver rodando"""
    try:
        tor_process = stem.process.launch_tor_with_config(
            config={
                'SocksPort': str(TOR_PORT),
                'ControlPort': str(CONTROL_PORT),
                'HashedControlPassword': '16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C',
            },
            take_ownership=True,
        )
        return tor_process
    except Exception as e:
        print("[INFO] Tor já está rodando ou ocorreu um erro ao iniciar:", e)
        return None

def openDriver():
    temp_profile = tempfile.mkdtemp()
    
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument(f"--user-data-dir={temp_profile}")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")
    
    # chrome_options.add_argument(f'--proxy-server=socks5://127.0.0.1:{TOR_PORT}')
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": random.choice(user_agents)})
    
    return driver

def clear_browser_data(driver):
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    print("[INFO] Dados do navegador limpos, simulando nova identidade.")

def loadPage(driver):
    driver.get(SITE_URL)

def close_cookie_banner(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.fc-button.fc-primary-button"))
        )
        driver.execute_script("document.querySelector('button.fc-button.fc-primary-button').click();")
        print("[INFO] Banner de cookies fechado com sucesso")
        return True
    except Exception as e:
        print(f"[AVISO] Não foi possível fechar o banner de cookies")
        return False

def click_read_more(driver):
    try:
        read_more_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.widget-btn"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", read_more_button)
        
        driver.execute_script("arguments[0].click();", read_more_button)
        print("[INFO] Botão 'Leia mais' clicado com sucesso")
        return True
    except Exception as e:
        print(f"[AVISO] Não foi possível clicar no botão Leia mais")
        return False

def vote(driver):
    try:
        print("[INFO] Aguardando o carregamento da enquete...")
        
        close_cookie_banner(driver)
        
        click_read_more(driver)

        
        print("[INFO] Aguardando o carregamento da enquete...")

        print("[INFO] Clicando na opção desejada...")
        checkbox = driver.find_element(By.ID, "choice-d6a33e0b-f11d-40d8-854b-b318f4cfa492-selector")
        driver.execute_script("arguments[0].click();", checkbox)  # usa JS para garantir o clique


        print("[INFO] Clicando no botão Votar...")
        vote_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "totalpoll-buttons-vote"))
        )
        driver.execute_script("arguments[0].click();", vote_button)

        if "obrigado" in driver.page_source.lower():
            print("[SUCESSO] Voto registrado com sucesso!")
            return True
        else:
            print("[AVISO] Possível falha no registro do voto")
            return False
            
    except Exception as e:
        print(f"[ERRO] Durante o voto: {e}")
        return False

def main():
    # tor_process = start_tor()
    
    try:
        while True:
            driver = openDriver()
            
            try:
                loadPage(driver)
                vote(driver)
                
                clear_browser_data(driver)
                    
            finally:
                driver.quit()
                
    except KeyboardInterrupt:
        print("\n[INFO] Encerrando script...")
        sys.exit()
    # finally:
        # if tor_process:
        #     tor_process.terminate()


running = True

def threaded_main(thread_id):
    while running:
        print(f"[THREAD {thread_id}] Iniciando ciclo...")
        driver = openDriver()

        try:
            loadPage(driver)
            vote(driver)
            clear_browser_data(driver)
        except Exception as e:
            print(f"[THREAD {thread_id}] Erro: {e}")
        finally:
            driver.quit()
            print(f"[THREAD {thread_id}] Navegador fechado.")
        

def start_threads(n=15):
    threads = []
    for i in range(n):
        t = threading.Thread(target=threaded_main, args=(i+1,))
        t.start()
        threads.append(t)
    return threads

if __name__ == "__main__":
    try:
        #get_new_tor_ip()    
        print("[INFO] Iniciando threads...")
        threads = start_threads()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Encerrando script...")
        running = False
        for t in threads:
            t.join()
        print("[INFO] Todas as threads encerradas com sucesso.")
        sys.exit()
