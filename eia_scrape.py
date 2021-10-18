from bs4 import BeautifulSoup
import requests
import pandas as pd

url = r'https://www.eia.gov/dnav/pet/pet_sum_sndw_dcus_nus_w.htm'
html = requests.get(url).content
soup = BeautifulSoup(html, 'html.parser')

# access html data cells
tds = soup.find_all('td', {'class': 'DataStub1'})

# find the text and the indent
texts = [td.contents[0] for td in tds]
indents = [td.find_previous('td').get('width') for td in tds]
indents = [int(ii) for ii in indents]

# find the source key; this should be a regex
urls = [td.find_next('a').get('href') for td in tds]
start, end = 32, -4
source_keys = [url[start:end] for url in urls]

# turn the indents into levels and then create a mapping lookup dict
uniques = sorted(list(set(indents)))
levels = list(range(len(uniques)))
level_lookup = dict(zip(uniques, levels))

# join it all up
triples = zip(texts, [level_lookup[indent] for indent in indents], source_keys)
triples = list(triples)

columns = ['text', 'level', 'source_key']
df = pd.DataFrame(data=triples, columns=columns)


print('hello world')


