# parser of all vacancies for python on hh.ru throughout Russia (only with the specified salary), with chart display.
import requests
from bs4 import BeautifulSoup as bs
import numpy
import pandas as pd
import matplotlib.pyplot as plt

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36 OPR/64.0.3417.54'}

base_url = 'https://hh.ru/search/vacancy?search_period=7&clusters=true&area=113&text=python&enable_snippets=true&page=0'


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
                url = f'https://hh.ru/search/vacancy?search_period=7&clusters=true&area=113&text=python&enable_snippets=true&page={i}'
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
                salary = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text.split('-')
                city = div.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
                new_salary = []
                salary_final = 0
                salary2 = []

                for item in salary:
                    # remove unicode
                    item = item.replace(u'\xa0', u' ')
                    new_salary.append(item)
                for item in new_salary:

                    if 'руб'in item:
                        # select numbers from a string
                        salary2.append(int(''.join(filter(str.isdigit, item))))
                        # calculation of arithmetic mean
                        salary_final = int(numpy.mean(salary2))

                    elif 'USD' in item:
                        salary2.append(int(''.join(filter(str.isdigit, item))))
                        new_item = numpy.mean(salary2)
                        # converting bucks into rubles
                        salary_final = int(new_item * 63.72)

                    elif item.find('EUR'):
                        salary2.append(int(''.join(filter(str.isdigit, item))))
                        new_item = numpy.mean(salary2)
                        # converting euros to rubles
                        salary_final = int(new_item * 71.13)

                jobs.append({
                    'salary': salary_final,
                    'city': city.split(',')[0],
                })

            except:
                pass

    else:
        print('DONE. Status code =  ' + str(request.status_code))
    return jobs


jobs = hh_parse(base_url, headers)

# Processing the data received in parsing. Grouping cities and calculate the average salary in a city
data = pd.DataFrame(jobs)
group_data = data.groupby('city')
average = group_data.mean()
average.to_csv('group_table.csv')

# Reading the input file. Processing data from the file to display a graph of average salaries by city
data = pd.read_csv('group_table.csv')

city_list = []
salary_list = []
for city in data['city']:
    city_list.append(city)

for salary in data['salary']:
    salary_list.append(int(salary))

fig = plt.gcf()
fig.canvas.set_window_title('Median salaries for Python developers in Russia')
fig.set_size_inches(18.5, 10.5)
plt.subplots_adjust(left=0.1, right=0.9, bottom=0.4, top=0.88)

plt.bar(city_list, salary_list, color='dodgerblue', alpha=0.7)

plt.xlabel('Median Salary', fontsize=16)
plt.xticks(rotation=90)

plt.title('Median salaries for Python developers in Russia', fontsize=16)
plt.grid(axis='y')

# Saving the figure on disk. 'dpi' and 'quality' can be adjusted according to the required image quality.
plt.savefig('Median_salary.png', dpi=400, quality=100)

# Displays the plot.
plt.show()


