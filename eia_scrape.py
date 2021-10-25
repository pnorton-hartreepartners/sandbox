'''
this script scrapes the eia weekly report directly from the web
in order to capture the indentation that defines the hierarchy
the output is a dataframe with:
- text description
- indent level
- indent change
- symbol
- the cumulative text including those from previous levels in the hierarchy
however, the report table name is missing; this will be derived by mapping the symbols
to internal metadata
'''

from bs4 import BeautifulSoup
import requests
import pandas as pd

url = r'https://www.eia.gov/dnav/pet/pet_sum_sndw_dcus_nus_w.htm'
html = requests.get(url).content
soup = BeautifulSoup(html, 'html.parser')

# access html data cells
tds = soup.find_all('td', {'class': 'DataStub1'})

# find the text and the indent
texts = [str(td.contents[0]) for td in tds]
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

# create a dataframe to set up the analysis
columns = ['text', 'level', 'source_key']
df = pd.DataFrame(data=triples, columns=columns)

# first order difference
df['level_change'] = df['level'] - df['level'].shift(periods=1, axis='index', fill_value=0)

# initialise column and change type to accept list
df['hierarchy'] = None
df['hierarchy'] = df['hierarchy'].astype('object')

content = []
for i, row in df.iterrows():
    # extend the list ie dont pop
    if row['level_change'] >= 1:
        pop_count = 0

    # even if the list length is unchanged, we pop once to replace with the new value
    else:
        pop_count = abs(row['level_change']) + 1

    # pop the required number of times
    for _ in range(pop_count):
        try:
            content.pop()
        except:
            pass

    # update the list and the df
    content.append(row['text'])
    df.at[i, 'hierarchy'] = content.copy()

df.to_clipboard()
print('hello world')


