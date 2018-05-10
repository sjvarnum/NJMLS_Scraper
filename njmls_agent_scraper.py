""" This version gets the list of municipalities from Wikipedia """


from bs4 import BeautifulSoup
import requests
import pandas as pd
import re


agent = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
)

wiki_url = 'https://en.wikipedia.org/wiki/List_of_municipalities_in_New_Jersey'
r = requests.get(wiki_url, headers={'User-Agent': agent})
c = r.content
soup = BeautifulSoup(c, 'html.parser')

municipalities = []
table = soup.find('table', attrs={'class': 'wikitable sortable'})
rows = table.find_all('tr')
for row in rows[1:]:
    cols = row.find_all('td')
    cols = [element.text.strip() for element in cols]
    my_dict = {}
    my_dict['City'] = cols[1]
    my_dict['County'] = cols[2]
    municipalities.append(my_dict)


base_url = 'http://www.njmls.com/members/index.cfm?action=dsp.results&city='

url_list = []
for item in municipalities:
    city = item['City']
    county = item['County']
    url = f'{base_url}{city}'.replace(' ', '+')
    url = f'{url}&county={county}'
    url_list.append(url)
url_list

agent_list = []
for url in url_list:

    r = requests.get(url, headers={'User-Agent': agent})
    c = r.content
    soup = BeautifulSoup(c, 'html.parser')
    agents = soup.find_all('div', {'class': 'realtor-info'})

    for i in agents[:-1]:
        my_dict = {}
        try:
            my_dict['Name'] = i.find('strong').text
        except (AttributeError, IndexError):
            None
        try:
            my_dict['Title'] = i.find('div').contents[0].replace(
                '\n', '').replace('\t', '')
        except (AttributeError, IndexError):
            None
        try:
            my_dict['Agency'] = i.find_all('strong')[1].text
        except (AttributeError, IndexError):
            None
        try:
            my_dict['Office Number'] = (i.find(
                string=re.compile('Office Phone:'))
                .replace('\n', '').replace('\t', '')
                .split(' ')[2].replace('(', '')
                .replace(')', '-') + i.find(
                string=re.compile('Office Phone:'))
                .replace('\n', '').replace('\t', '').split(' ')[-1])
        except (AttributeError, IndexError):
            None

        try:
            my_dict['Contact Number'] = (i.find(
                string=re.compile('Contact Phone:'))
                .replace('\n', '').replace('\t', '')
                .split()[2].replace('(', '')
                .replace(')', '-') + i.find(
                string=re.compile('Contact Phone:'))
                .replace('\n', '').replace('\t', '').split()[-1])
        except (AttributeError, IndexError):
            None

        try:
            my_dict['Email'] = (i.find('a', {'class': 'tips'})
                                .get('href').split(':')[1].split('?')[0])
        except (AttributeError, IndexError):
            None
        agent_list.append(my_dict)

df = pd.DataFrame(agent_list)
agent_df = df[['Name', 'Title', 'Agency', 'Office Number',
               'Contact Number', 'Email']].drop_duplicates()
agent_df.to_csv('njmls_agents_20180509.csv', index=False)
