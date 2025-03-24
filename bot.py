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

# Configuração do Tor
TOR_PORT = 9050
CONTROL_PORT = 9051
TOR_PASSWORD = "123"  # Altere para a senha que configurou no Tor

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
    """Abre o navegador Chrome configurado para usar o Tor com uma nova identidade"""
    temp_profile = tempfile.mkdtemp()
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"--user-data-dir={temp_profile}")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--incognito")
    
    # Configura o proxy para usar o Tor
    chrome_options.add_argument(f'--proxy-server=socks5://127.0.0.1:{TOR_PORT}')
    
    # Configurações adicionais para evitar detecção
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Altera o user-agent para parecer mais humano
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": random.choice(user_agents)})
    
    return driver

def clear_browser_data(driver):
    """Limpa cookies, localStorage e sessionStorage para simular nova identidade"""
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    print("[INFO] Dados do navegador limpos, simulando nova identidade.")

def loadPage(driver):
    """Carrega a página da enquete"""
    driver.get("https://www.bastidoresdapoliticapb.com.br/enquete/")
    # Espera aleatória para simular comportamento humano

def vote(driver):
    """Realiza o voto na enquete"""
    try:
        print("[INFO] Aguardando opções da enquete...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".apm-choosing"))
        )
        

        print(f"[INFO] Clicando na opção {3}...")
        driver.execute_script(f"""
            document.querySelectorAll('.apm-choosing input[type="radio"]')[{2}].click();
        """)
        
        print("[INFO] Enviando voto...")
        driver.execute_script("""
            document.querySelector('.ays_finish_poll').click();
        """)
    

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
    tor_process = start_tor()
    
    try:
        while True:
            print("\n" + "=" * 50)
            print("[INFO] Iniciando novo ciclo de voto")
            
            # Obtém um novo IP via Tor
            get_new_tor_ip()
            print("[INFO] Novo circuito Tor estabelecido (novo IP)")
            
            driver = openDriver()
            
            try:
                loadPage(driver)
                vote(driver)
                
                # Limpa os dados do navegador para simular nova identidade
                clear_browser_data(driver)
                    
            finally:
                driver.quit()
                
    except KeyboardInterrupt:
        print("\n[INFO] Encerrando script...")
    finally:
        if tor_process:
            tor_process.terminate()

while True:
    main()
