#!/usr/bin/env python
# coding: utf-8
import numpy
import scipy
import sklearn
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os
from pathlib import Path
import random
import sys

# Load the data
trade_paths = []
year = '2018'
folder = '/Users/jack/Documents/University/year2/CS261/CS261-Group19/cs261dummydata'
for path in Path(f'{folder}/derivativeTrades/{year}/January').rglob('*.csv'):
    trade_paths.append(path)
good_trades_df = pd.concat([pd.read_csv(f) for f in trade_paths])
good_trades_df.astype({'quantity': 'int64'}).dtypes

good_trades_df['erroroneous'] = good_trades_df.apply(lambda x: 'good', axis=1)

del good_trades_df['tradeID']
del good_trades_df['notionalAmount']
del good_trades_df['notionalCurrency']
del good_trades_df['underlyingCurrency']
del good_trades_df['underlyingPrice']
del good_trades_df['maturityDate']
del good_trades_df['dateOfTrade']

bad_trades_df = good_trades_df.copy()

multipliers = [10, 100, 1000, (1/2), (1/3), (1/5), (1/10), (1/100)]

def multiply(quant):
    new_quant = 0
    while new_quant == 0:
        new_quant = quant * random.choice(multipliers)
        if new_quant > sys.maxsize:
            new_quant = 0
        else:
            break
    return new_quant

for row in bad_trades_df.itertuples():
    quantity = row.quantity
    new_quantity = multiply(quantity)
    bad_trades_df.at[row.Index, 'quantity'] = new_quantity
    bad_trades_df.at[row.Index, 'erroroneous'] = 'bad'

trades = pd.concat([good_trades_df, bad_trades_df])
print(trades)