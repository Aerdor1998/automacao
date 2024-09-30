import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_infojobs_companies(url):
    # Fazer a requisição HTTP
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar todos os cards de empresas
    company_cards = soup.find_all('div', class_='card border-transparent card-shadow mb-16')

    companies = []

    for card in company_cards:
        # Extrair informações de cada card
        name = card.find('div', class_='h3 text-body font-weight-bold').text.strip()
        sector = card.find('div', class_='text-medium text-body').text.strip()
        
        # Extrair número de vagas (se disponível)
        vacancies_elem = card.find('a', class_='')
        vacancies = vacancies_elem.text.strip() if vacancies_elem else 'N/A'
        
        # Extrair avaliação
        rating_elem = card.find('span', class_='font-weight-bold text-body headings-font-family')
        rating = rating_elem.text.strip() if rating_elem else 'N/A'
        
        # Extrair número de avaliações
        reviews_elem = card.find('div', class_='text-medium')
        reviews = reviews_elem.text.strip() if reviews_elem else 'N/A'
        
        # Adicionar à lista de empresas
        companies.append({
            'Nome': name,
            'Setor': sector,
            'Vagas': vacancies,
            'Avaliação': rating,
            'Número de Avaliações': reviews
        })

    return companies

def main():
    url = "https://www.infojobs.com.br/empresas"
    companies = scrape_infojobs_companies(url)
    
    # Criar um DataFrame com os dados
    df = pd.DataFrame(companies)
    
    # Salvar como CSV
    df.to_csv('infojobs_companies.csv', index=False)
    print(f"Dados de {len(companies)} empresas foram salvos em 'infojobs_companies.csv'")

    # Exibir as primeiras linhas do DataFrame
    print(df.head())

if __name__ == "__main__":
    main()