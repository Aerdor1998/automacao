from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import logging
import json
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IBGEScraper:
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        self.service = Service(ChromeDriverManager().install())
        self.driver = None

    def iniciar_driver(self):
        if self.driver is None:
            self.driver = webdriver.Chrome(service=self.service, options=self.options)
        logging.info("Driver do Chrome iniciado.")

    def scrape_municipio(self, codigo_municipio, max_tentativas=3):
        url = f"https://cidades.ibge.gov.br/brasil/sp/{codigo_municipio}/panorama"
        
        for tentativa in range(max_tentativas):
            logging.info(f"Tentativa {tentativa + 1} de {max_tentativas}")
            try:
                self.iniciar_driver()
                self.driver.get(url)
                logging.info(f"Página carregada: {url}")

                # Espera dinâmica para qualquer elemento que indique que a página carregou
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Espera adicional para garantir que o JavaScript carregou o conteúdo
                time.sleep(15)

                # Injetar JavaScript para extrair dados
                dados = self.extrair_dados_via_js()
                dados['Cod. Municipio'] = codigo_municipio
                return dados
            except Exception as e:
                logging.error(f"Erro na tentativa {tentativa + 1}: {str(e)}")
                if tentativa == max_tentativas - 1:
                    logging.error("Número máximo de tentativas atingido.")
                    return None
                time.sleep(5)
            finally:
                self.fechar_driver()

    def extrair_dados_via_js(self):
        script = """
        function extrairDados() {
            var dados = {};
            var indicadores = [
                "População estimada",
                "Salário médio mensal dos trabalhadores formais",
                "Matrículas no ensino fundamental",
                "PIB per capita",
                "Taxa de mortalidade infantil"
            ];
            
            indicadores.forEach(function(indicador) {
                var elemento = document.evaluate(
                    "//div[contains(text(), '" + indicador + "')]/following-sibling::div",
                    document,
                    null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                    null
                ).singleNodeValue;
                
                dados[indicador] = elemento ? elemento.textContent.trim() : "Não encontrado";
            });
            
            var breadcrumb = document.querySelector('.breadcrumb');
            if (breadcrumb) {
                var items = breadcrumb.querySelectorAll('li');
                if (items.length >= 3) {
                    dados['UF'] = items[items.length - 2].textContent.trim();
                    dados['Municipio'] = items[items.length - 1].textContent.trim();
                }
            }
            
            return JSON.stringify(dados);
        }
        return extrairDados();
        """
        resultado = self.driver.execute_script(script)
        return json.loads(resultado)

    def determinar_tamanho(self, dados):
        if "População estimada" in dados:
            populacao = ''.join(filter(str.isdigit, dados["População estimada"]))
            if populacao:
                pop = int(populacao)
                if pop < 50000:
                    return "Pequeno"
                elif 50000 <= pop < 100000:
                    return "Médio"
                else:
                    return "Grande"
        return "Não foi possível determinar"

    def fechar_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
        logging.info("Driver do Chrome fechado.")

def main():
    scraper = IBGEScraper()
    codigo_municipio = "3550308"  # Código de São Paulo
    dados = scraper.scrape_municipio(codigo_municipio)
    if dados:
        dados["Tamanho"] = scraper.determinar_tamanho(dados)
        for chave, valor in dados.items():
            print(f"{chave}: {valor}")
    else:
        print("Não foi possível obter os dados do município.")

if __name__ == "__main__":
    main()