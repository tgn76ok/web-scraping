import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configurações
SITE_URL = "https://www.polemicaparaiba.com.br/politica/enquete-polemica-paraiba-em-quem-voce-votaria-para-ser-o-proximo-governador-da-paraiba/"
CANDIDATE_ID = "choice-d6a33e0b-f11d-40d8-854b-b318f4cfa492-selector"
THRESHOLD = 8.0
PERFIL_DIR = Path("./meu_perfil_chromium")

def iniciar_votacao():
    with sync_playwright() as p:
        print("Iniciando navegador com perfil persistente...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(PERFIL_DIR),
            headless=False,
            executable_path="/usr/bin/google-chrome"
        )
        page = browser.new_page()
        page.goto(SITE_URL, timeout=60000)

        # Checagem inicial para contornar manualmente o Cloudflare
        if "checking your browser" in page.content().lower():
            input("🚧 Passe pelo Cloudflare manualmente e pressione ENTER para continuar...")

        try:
            print("⏳ Aguardando carregamento e aceitação de cookies...")
            try:
                page.click("button.fc-button.fc-primary-button", timeout=3000)
            except:
                pass

            print("➡️ Expandindo enquete...")
            try:
                page.click("button.widget-btn", timeout=3000)
            except:
                pass

            print("🗳️ Selecionando candidato...")
            page.click(f"#{CANDIDATE_ID}")

            print("✅ Votando...")
            page.click(".totalpoll-buttons-vote", timeout=3000)

            time.sleep(2)  # Aguarda resultado

            if "obrigado" in page.content().lower():
                print("🎉 Voto registrado com sucesso!")
            else:
                print("⚠️ Não foi possível confirmar o voto!")

            print("📊 Verificando liderança...")
            textos = page.query_selector_all(".totalpoll-question-choices-item-votes-text")
            percentuais = []

            for t in textos:
                try:
                    valor = float(t.inner_text().replace("%", "").strip())
                    percentuais.append(valor)
                except:
                    continue

            if len(percentuais) >= 2:
                percentuais.sort()
                diff = percentuais[-1] - percentuais[-2]
                print(f"🏁 Liderança atual: {diff:.2f}%")
                if diff > THRESHOLD:
                    print(f"✅ Liderança superior a {THRESHOLD}%. Fim da automação.")
            else:
                print("❌ Não foi possível determinar os percentuais.")
        finally:
            page.close()
            browser.close()

if __name__ == "__main__":
    iniciar_votacao()
