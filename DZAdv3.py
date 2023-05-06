import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
import re
import json


def get_headers():
    return Headers(browser='firefox', os='win').generate()


hh_main = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=get_headers()).text
hh_soup = BeautifulSoup(hh_main, 'lxml')

tag_all_vacancy = hh_soup.find('main', class_='vacancy-serp-content')
tag_vacancy = tag_all_vacancy.find_all('a', class_='serp-item__title')

parsed_data = []

for vacancy in tag_vacancy:
    links = vacancy['href']
    links = re.findall(r'https://spb.hh.ru/vacancy/\d+', links)
    for link in links:
        vacancy_main = requests.get(link, headers=get_headers()).text
        disc_vacancy_soup = BeautifulSoup(vacancy_main, 'lxml')
        salary = disc_vacancy_soup.find('span', class_='bloko-header-section-2 bloko-header-section-2_lite').text
        company_name = disc_vacancy_soup.find('span', 'vacancy-company-name').text
        city_p = disc_vacancy_soup.find('p', attrs={'data-qa': 'vacancy-view-location'})
        city_span = disc_vacancy_soup.find('span', attrs={'data-qa': 'vacancy-view-raw-address'})

        if city_p:
            city = city_p.text
        elif city_span:
            city = city_span.text
        else:
            city = "Город не указан"

        disc_text = re.findall(r'.*Django.*Flask.*|.*Flask.*Django.*', disc_vacancy_soup.find('div', class_='vacancy-section').text)
        for disc_text in disc_text:
            parsed_data.append(
                {
                'Ссылка': link + '\n',
                 'Зарплата': salary + '\n',
                 'Название компании': company_name + '\n',
                 'Город': city + '\n'
                }
            )

parsed_data_str = json.dumps(parsed_data)

with open("vacancy.json", "w", encoding='utf-8') as f:
    f.write(parsed_data_str.encode('utf-8').decode('unicode_escape'))
