import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import tempfile

temp_profile = tempfile.mkdtemp()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"--user-data-dir={temp_profile}")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-cache")
chrome_options.add_argument("--incognito")

def openDriver():
    driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
    return driver

def loadPage(driver):
    driver.get("https://www.bastidoresdapoliticapb.com.br/enquete/")

def main():
    try:
        driver = openDriver()
        print("[INFO] Iniciando navegador...")
        
        loadPage(driver)
        print("[INFO] Página carregada.")


        print("[INFO] Aguardando opções da enquete...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".apm-choosing"))
        )
        print("[INFO] Opções carregadas.")

        print("[INFO] Clicando na 3ª opção...")
        driver.execute_script("""
            document.querySelectorAll('.apm-choosing input[type="radio"]')[2].click();
        """)

        print("[INFO] Enviando voto...")
        driver.execute_script("""
            document.querySelector('.ays_finish_poll').click();
        """)


    except Exception as e:
        print(f"[ERRO] {e}")

    finally:
        print("[INFO] Fechando navegador...")
        driver.quit()

for i in range(10):
    main()
