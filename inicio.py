from selenium import webdriver
from time import sleep,time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


start_time = time()
chrome_options = webdriver.ChromeOptions()

# chrome_options.add_argument("--disable-images")
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-cache")
chrome_options.page_load_strategy = 'eager'

navegador = webdriver.Chrome(options=chrome_options)

navegador.get("sua urls")

# WebDriverWait(navegador, 25).until(EC.element_to_be_clickable((By.ID,"choice-713b8dc9-0de5-4623-9005-f5971115fd4c-selector")))
# WebDriverWait(navegador, 25).until(EC.element_to_be_clickable((By.XPATH,"/div[4]/button")))



# Aguarda até que o elemento esteja presente na página
js_code = "document.getElementById('choice-713b8dc9-0de5-4623-9005-f5971115fd4c-selector').click();"
navegador.execute_script(js_code)
print('olamniudoasdfdasgf')
js_code1 = "document.querySelector('button.totalpoll-button.totalpoll-button-primary.totalpoll-buttons-vote').click();"
navegador.execute_script(js_code1)

print(f"Tempo de execução: {time() - start_time} segundos")
# Fecha o navegador ao finalizar
sleep(10)
navegador.quit()




