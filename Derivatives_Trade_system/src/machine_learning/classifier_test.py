#!/usr/bin/env python
# coding: utf-8
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
import pandas as pd
from pathlib import Path
import random
import sys
import numpy as np
from sklearn import metrics
from sklearn.model_selection import train_test_split

# Load the data
trade_paths = []
year = '2018'
folder = '/Users/jack/Documents/University/year2/CS261/CS261-Group19/cs261dummydata'
for path in Path(f'{folder}/derivativeTrades/{year}/January').rglob('*.csv'):
    trade_paths.append(path)
good_trades_df = pd.concat([pd.read_csv(f) for f in trade_paths])
good_trades_df.astype({'quantity': 'int64'}).dtypes

good_trades_df['erroroneous'] = good_trades_df.apply(lambda x: 1, axis=1)

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

def handle_non_numerical_data(df):
    columns = df.columns.values
    for column in columns:
        text_digit_vals = {}
        def convert_to_int(val):
            return text_digit_vals[val]

        if df[column].dtype != np.int64 and df[column].dtype != np.float64:
            column_contents = df[column].values.tolist()
            unique_elements = set(column_contents)
            x = 0
            for unique in unique_elements:
                if unique not in text_digit_vals:
                    text_digit_vals[unique] = x
                    x+=1

            df[column] = list(map(convert_to_int, df[column]))

    return df

for row in bad_trades_df.itertuples():
    quantity = row.quantity
    new_quantity = multiply(quantity)
    bad_trades_df.at[row.Index, 'quantity'] = new_quantity
    bad_trades_df.at[row.Index, 'erroroneous'] = 0

trades = pd.concat([good_trades_df, bad_trades_df])
trades = handle_non_numerical_data(trades)

y = trades.iloc[:,5]
X = trades.iloc[:,:5]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, shuffle=True)

classifiers = {}

classifiers['LR'] = LogisticRegression(random_state=0, solver='lbfgs', multi_class='ovr', max_iter=10000).fit(X, y)
classifiers['SGD'] = SGDClassifier(max_iter=1000, tol=1e-3)
classifiers['LinearSVC'] = LinearSVC(random_state=0, tol=1e-5, max_iter=5000)


for name, clf in classifiers.items(): 
    clf.fit(X_train, y_train)
    metric = clf.score(X_test, y_test)
    print(f"Classification score for classifier {name}:{metric}")
