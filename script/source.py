import pandas as pd
from utils.finance_data import fetch_history

url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
table = pd.read_html(url)
sp500_df = table[0]  # Le premier tableau contient les données

df = sp500_df[['Symbol', 'Security']]
dfa = []

for _,symbol in df.iterrows() : 
    print(symbol['Symbol'])