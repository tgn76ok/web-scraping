from selenium import webdriver
from time import sleep,time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException

from selenium.webdriver.support import expected_conditions as EC
from threading import Thread
def votar():
    chrome_options = webdriver.ChromeOptions()
    # proxy = '200.155.180.166:8080'
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-cache")
    # chrome_options.add_argument(f"--proxy-server={proxy}")
    chrome_options.page_load_strategy = 'eager'

    navegador = webdriver.Chrome(options=chrome_options,service=Service(ChromeDriverManager().install()))

    start_time = time()
    navegador.get("https://www.polemicaparaiba.com.br/politica/enquete-polemica-paraiba-em-que-voce-votaria-para-governar-a-paraiba-caso-as-eleicoes-de-2026-fossem-hoje-participe/?utm_source=whatsapp&utm_medium=referral&utm_campaign=share_alongisde")
    # WebDriverWait(navegador, 25).until(EC.element_to_be_clickable((By.ID,"choice-713b8dc9-0de5-4623-9005-f5971115fd4c-selector")))
    # WebDriverWait(navegador, 25).until(EC.element_to_be_clickable((By.XPATH,"/div[4]/button")))

    # Aguarda até que o elemento esteja presente na página
    try:
        js_code = "document.getElementById('choice-7ac78479-8853-456d-9a67-614dc38fd10f-selector').click();"
        navegador.execute_script(js_code)
        sleep(2)
        js_code1 = "document.querySelector('button.totalpoll-button.totalpoll-button-primary.totalpoll-buttons-vote').click();"
        navegador.execute_script(js_code1)

        print(f'--------------------------')
        print(f'Processor deu bom')
        print(f'--------------------------')
        print(f"Tempo de execução: {time() - start_time} segundos")
        # Fecha o navegador ao finalizar
    except WebDriverException as e:
        print("erro")
        print(f'Processor deu ruim')
        new = str(e).split('Stacktrace')[0]
        new = str(e).split('\n')[0]
        print(f"Tempo de execução: {time() - start_time} segundos")
        print(new)
        sleep(100)
    navegador.quit()




while True:
    votar()
