# делаю парсер всех вакансий по питону на hh по всей России(в данный момент для удобства только 1 город).Только с указанной зарплатой
import requests
import csv
from bs4 import BeautifulSoup as bs
import pprint
import numpy

# обязательно нужно указать:
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36 OPR/64.0.3417.54'}

base_url = 'https://hh.ru/search/vacancy?search_period=3&clusters=true&area=113&text=python&enable_snippets=true&page=0'


def hh_parse(base_url, headers):
    jobs = []
    urls = []
    urls.append(base_url)
    session = requests.Session()
    request = session.get(base_url, headers=headers)

    if request.status_code == 200:
        soup = bs(request.content, 'lxml')
        try:
            pagination = soup.find_all('a', attrs={'data-qa': 'pager-page'})
            count = int(pagination[-1].text)
            for i in range(count):
                url = f'https://hh.ru/search/vacancy?search_period=3&clusters=true&area=113&text=python&enable_snippets=true&page={i}'
                if url not in urls:
                    urls.append(url)
        except:
            pass

    for url in urls:
        request = session.get(url, headers=headers)
        soup = bs(request.content, 'lxml')
        divs = soup.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'})
        for div in divs:
            try:
                title = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
                href = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
                salary = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text.split('-')
                city = div.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
                new_salary = []
                salary_final = 0
                salary2 = []

                for item in salary:
                    # убираем юникод
                    item = item.replace(u'\xa0', u' ')
                    new_salary.append(item)
                for item in new_salary:

                    if 'руб'in item:
                        # выбираем цифры из строки
                        salary2.append(int(''.join(filter(str.isdigit, item))))
                        # считаем среднее арифметическое
                        salary_final = int(numpy.mean(salary2))

                    elif 'USD' in item:
                        salary2.append(int(''.join(filter(str.isdigit, item))))
                        new_item = numpy.mean(salary2)
                        # ребеводим баксы в рубли
                        salary_final = int(new_item * 63.72)

                    elif item.find('EUR'):
                        salary2.append(int(''.join(filter(str.isdigit, item))))
                        new_item = numpy.mean(salary2)
                        # переводим евро в рубли
                        salary_final = int(new_item * 71.13)

                jobs.append({
                    'title': title,
                    'href': href,
                    'salary': salary_final,
                    'city': city,
                })
            except:
                pass
            pprint.pprint(jobs)
    else:
        print('DONE. Status code =  ' + str(request.status_code))
    return jobs


def files_writer(jobs):
    with open('parsed_jobs.csv', 'w')as file:
        a_pen = csv.writer(file)
        a_pen.writerow(('Город', 'Вакансия', 'Зарплата', 'Ссылка'))
        for job in jobs:
            a_pen.writerow((job['city'], job['title'], job['salary'], job['href']))


jobs = hh_parse(base_url, headers)
files_writer(jobs)
