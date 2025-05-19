import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from stem import Signal
from stem.control import Controller
import random
import threading

# Configurações
TOR_PORT = 9050
CONTROL_PORT = 9051
TOR_PASSWORD = "123"
SITE_URL = 'https://www.polemicaparaiba.com.br/politica/enquete-polemica-paraiba-em-quem-voce-votaria-para-ser-o-proximo-governador-da-paraiba/'
CICERO_ID = "choice-d6a33e0b-f11d-40d8-854b-b318f4cfa492-selector"
running = True

def get_new_tor_ip():
    """Muda o IP através do Tor"""
    with Controller.from_port(port=CONTROL_PORT) as controller:
        controller.authenticate(password=TOR_PASSWORD)
        controller.signal(Signal.NEWNYM)
        time.sleep(controller.get_newnym_wait())

def openDriver():
    """Abre o navegador com configurações anti-detecção"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")
    # chrome_options.add_argument(f'--proxy-server=socks5://127.0.0.1:{TOR_PORT}')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # User-Agent aleatório
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": random.choice(user_agents)})
    
    return driver

def get_current_lead(driver):
    try:    
        percentages = {}
        choices = driver.find_elements(By.CLASS_NAME, "totalpoll-question-choices-item")
        for choice in choices:
            name = choice.find_element(By.CLASS_NAME, "totalpoll-question-choices-item-label").text.split('\n')[0].strip()
            percent = choice.find_element(By.CLASS_NAME, "totalpoll-question-choices-item-votes-text").text.replace('%', '').strip()
            
            percentages[name] = float(percent)
        

        cicero = percentages.get("Cícero Lucena", 0)
        others = [v for k, v in percentages.items() if k != "Cícero Lucena"]
        return cicero - max(others) if others else 0
    
    except Exception as e:
        print(f"[ERRO] Ao verificar liderança: {str(e)}")
        return None

def execute_vote(driver):
    """Executa o voto e retorna a diferença percentual"""
    try:
        driver.get(SITE_URL)
        
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fc-button.fc-primary-button"))
            ).click()
        except:
            pass
        
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.widget-btn"))
            ).click()
        except:
            pass
        
        # Votar
        checkbox = driver.find_element(By.ID, CICERO_ID)
        driver.execute_script("arguments[0].click();", checkbox)

        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "totalpoll-buttons-vote"))
        ).click()
        
        time.sleep(2)  # Esperar atualização
        
        percentage = get_current_lead(driver)
        print(f"[INFO] Liderança atual: {percentage:.2f}%")
        return percentage
    
    except Exception as e:
        print(f"[ERRO] Durante o voto: {str(e)}")
        return None

def voting_loop(thread_id):
    while running:
        try:
            driver = openDriver()
            
            lead = execute_vote(driver)
            if lead is not None:
                if lead > 5:
                    print(f"[THREAD {thread_id}] ✅ Liderança de {lead}%. Aguardando 30 minutos...")
                    time.sleep(1800)  # Pausa longa
                else:
                    print(f"[THREAD {thread_id}] ⚠️ Liderança de {lead}%. Continuando...")
            
            driver.quit()
        
        except Exception as e:
            print(f"[THREAD {thread_id}] ❌ Erro crítico: {str(e)}")
            time.sleep(60)

threads = []
for i in range(10):
    t = threading.Thread(target=voting_loop, args=(i+1,))
    t.start()
    threads.append(t)

try:
    while True: 
        time.sleep(1)
except KeyboardInterrupt:
    running = False
    for t in threads: 
        t.join()