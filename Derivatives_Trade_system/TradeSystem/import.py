from pathlib import Path
import pandas as pd
import sqlite3 

cur = []
product = []
stock = []
folder = '../../Data' 
#replace folder with directory of files
#data should be the folder containing the dataset items
#looks like this C:\Users\Admin\Documents\cs261\Data\currencyValues
# C:\Users\Admin\Documents\cs261\Data\productPrices
# C:\Users\Admin\Documents\cs261\Data\currencyValues
#takes like 30seconds, pretty sure I could speed this up if I wasn't lazy.


files = [f'{folder}/companyCodes.csv',f'{folder}/productSellers.csv']

for path in Path(f'{folder}/currencyValues').rglob('*.csv'):
    files.append(path)
for path in Path(f'{folder}/productPrices').rglob('*.csv'):
    files.append(path)
for path in Path(f'{folder}stockPrices').rglob('*.csv'):
    files.append(path)

for f in files:
    op = open(f)
    rep = op.read().replace('/','-')
    op.close()

    op = open(f,'w')
    op.write(rep)
    op.close() #replaces all / with - so django recognises runs in like 5s this has next to no impact on performance

con = sqlite3.connect('db.sqlite3')
''' Importing all the values'''

for path in Path(f'{folder}/currencyValues').rglob('*.csv'):
	cur.append(path)
combined_csv = pd.concat([pd.read_csv(f) for f in cur])
combined_csv["date"] = pd.to_datetime(combined_csv["date"]).dt.strftime('%Y-%m-%d')
combined_csv.to_sql('trades_currency',con,if_exists='append',index=False)

for path in Path(f'{folder}/productPrices').rglob('*.csv'):
	product.append(path)
combined_product = pd.concat([pd.read_csv(f) for f in product])
combined_product["date"] = pd.to_datetime(combined_product["date"]).dt.strftime('%Y-%m-%d')
combined_product.to_sql('trades_productprices',con,if_exists='append',index=False)

for path in Path(f'{folder}/stockPrices').rglob('*.csv'):
   stock.append(path)
combined_stock = pd.concat([pd.read_csv(f) for f in stock])
combined_stock.rename(columns={'companyID':'companyID_id'},inplace=True)
combined_stock["date"] = pd.to_datetime(combined_stock["date"]).dt.strftime('%Y-%m-%d')
combined_stock.to_sql('trades_stockprices',con,if_exists='append',index=False)

codes = pd.read_csv(f'{folder}/companyCodes.csv')
codes.rename(columns={' companyTradeID':'companyID'}, inplace=True)
codes.to_sql('trades_company',con,if_exists='append',index=False)

sellers = pd.read_csv(f'{folder}/productSellers.csv')
sellers.rename(columns={'companyID':'companyID_id'},inplace=True)
sellers.to_sql('trades_productssold',con,if_exists='append',index=False)

con.close()
