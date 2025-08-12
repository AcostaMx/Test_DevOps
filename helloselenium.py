from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selectolax.parser import HTMLParser
import time

# URLs de productos
url_mlibre = [
    'https://www.mercadolibre.com.mx/mesa-plegable-plastico-tablon-portatil-tipo-portafolio-180-color-blanco/p/MLM47003664',
    'https://www.mercadolibre.com.mx/goxawee-potente-profesional-duradero-taladro-rotomartillo-cincelador-demoledor-rompedor-concreto-g5361-sds-plus-2200w-naranja-930rpm-5300bpm-con-cinceles/p/MLM43896493',
    'https://www.mercadolibre.com.mx/lapiz-optico-stylus-pluma-capacitivo-universal-para-ipad-android-tablet-celular-carga-rapidamagnetica-qyju-lapiz-optico-color-blanco-dibujo-escritura-digital/p/MLM44553853'
]


print("Hello Test Plans")

def get_webpage(driver, url):
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ui-pdp-title"))
        )
    except TimeoutException:
        print(f"Error: No se encontró el título en {url}")
    return driver.page_source

def get_content(html):
    data = HTMLParser(html)
    title_elem = data.css_first(".ui-pdp-title")
    price_elem = data.css_first(".andes-money-amount__fraction")  # Precio principal
    rating_elem = data.css_first("p.ui-pdp-review__amount")       # Número de calificaciones

    return {
        "title": title_elem.text(strip=True) if title_elem else "No encontrado",
        "price": price_elem.text(strip=True) if price_elem else "No disponible",
        "rating": rating_elem.text(strip=True) if rating_elem else "Sin calificaciones"
    }

if __name__ == '__main__':
    # Lista de navegadores a probar
    browsers = ["chrome", "firefox", "edge"]

    # Opciones comunes
    options_map = {
        "chrome": webdriver.ChromeOptions(),
        "firefox": webdriver.FirefoxOptions(),
        "edge": webdriver.EdgeOptions()
    }

    # Añadir argumentos necesarios
    for opts in options_map.values():
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--remote-allow-origins=*')

    # URL del Selenium Grid
    hub_url = "http://localhost:4444"

    for browser in browsers:
        print(f"\n🚀 Ejecutando pruebas en {browser.upper()}...\n")
        driver = None
        try:
            options = options_map[browser]
            driver = webdriver.Remote(command_executor=hub_url, options=options)
            print(f"✅ Conectado al nodo {browser.upper()} en el Grid")

            datos = []
            for url in url_mlibre:
                print(f"  Accediendo a: {url}")
                html = get_webpage(driver, url)
                content = get_content(html)
                datos.append({
                    "browser": browser,
                    "url": url,
                    "data": content
                })
                time.sleep(1)  # Pausa corta entre URLs

            # Mostrar resultados
            for item in datos:
                print(f"  [{item['browser']}] {item['data']['title']}")
                print(f"      Precio: {item['data']['price']} | Calificaciones: {item['data']['rating']}")

        except Exception as e:
            print(f"❌ Error con {browser}: {e}")
        finally:
            if driver:
                driver.quit()
            print(f"⏹ Pruebas en {browser.upper()} finalizadas.\n")
            time.sleep(2)  # Pausa entre navegadores

    print("✅ Todas las pruebas han terminado.")
