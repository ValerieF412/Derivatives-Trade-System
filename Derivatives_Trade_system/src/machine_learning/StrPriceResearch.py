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
import seaborn as sns

# Load the data

trades = []

folder = '/Users/mac/desktop/cs261dummydata'
for path in Path(f'{folder}/derivativeTrades').rglob('*.csv'):
    trades.append(path)
good_trades_df = pd.concat([pd.read_csv(f) for f in trades])
good_trades_df.astype({'quantity': 'int64'}).dtypes

good_trades_df['noerror'] = good_trades_df.apply(lambda x: 1, axis=1)

del good_trades_df['tradeID']
del good_trades_df['notionalAmount']
del good_trades_df['notionalCurrency']
del good_trades_df['underlyingCurrency']
del good_trades_df['underlyingPrice']
del good_trades_df['maturityDate']
del good_trades_df['dateOfTrade']

bad_trades_df = good_trades_df.copy()

multipliers = [10, 100, 1000, (1/2), (1/3), (1/5), (1/10), (1/100)]

def multiply(strike):
    new_strike = 0
    while new_strike == 0:
        new_strike = strike * random.choice(multipliers)
        if new_strike > sys.maxsize:
            new_strike = 0
        else:
            break
    return new_strike


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
    strike = row.strikePrice
    new_strike = multiply(strike)
    bad_trades_df.at[row.Index, 'strikePrice'] = new_strike
    bad_trades_df.at[row.Index, 'noerror'] = 0
#good_trades_df.info()
#bad_trades_df.info()
data = pd.concat([good_trades_df, bad_trades_df])
data = handle_non_numerical_data(data)
data.info()
data.head(5)
#print(good_trades_df)
#print(bad_trades_df)
print(data)

from sklearn.model_selection import train_test_split
y =data.iloc[:,5]
X =data.iloc[:,:5]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True, random_state = 0)
print(X_train.shape)
print(y_train.shape)
data.describe()

strike = data["strikePrice"]
mean = strike.mean()
std = strike.std()
def normfun(x,mu,sigma):
    pdf = np.exp(-((x - mu)**2)/(2*sigma**2)) / (sigma * np.sqrt(2*np.pi))
    return pdf

x = np.arange(data['strikePrice'].min(),data['strikePrice'].min(),10)

y = normfun(x, mean, std)
plt.plot(x,y)

plt.hist(strike, bins=10, rwidth=0.9, normed=True)
plt.title('Strike Price distribution')
plt.xlabel('Strike Price')
plt.ylabel('Amount')
#??????
plt.show()
data.describe()



#using minmax to normalise data
from sklearn import preprocessing

df_quantity = pd.DataFrame(data,columns=['quantity'])
df_strike = pd.DataFrame(data,columns=['strikePrice'])

# 2. create a min max processing object

min_max_scaler = preprocessing.MinMaxScaler()
scaled_array_quantity = min_max_scaler.fit_transform(df_quantity)
scaled_array_strike = min_max_scaler.fit_transform(df_strike)
# 3. convert the scaled array to dataframe

df__quantity_normalized = pd.DataFrame(scaled_array_quantity)
df__strike_normalized = pd.DataFrame(scaled_array_strike)
#print(df_normalized)


data['quantity']=df__quantity_normalized
data['strikePrice']=df__strike_normalized
#print(data['strikePrice'])
#data.describe()



corrDf=pd.DataFrame()
corrDf=data.corr()
corrDf['noerror'].sort_values(ascending=True)


plt.figure(figsize=(8,8))
sns.heatmap(data[["product","buyingParty","sellingParty","quantity","strikePrice","noerror"]].corr(),cmap='BrBG', annot=True,
           linewidths=.5)
plt.xticks(rotation=5)



from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier
from sklearn.svm import LinearSVC
from sklearn import metrics
from sklearn.model_selection import GridSearchCV,cross_val_score,StratifiedKFold
from sklearn.ensemble import VotingClassifier

#set kfold, using cross validation
kfold=StratifiedKFold(n_splits=10)
classifiers = []
classifiers.append(LinearSVC(dual=False))
classifiers.append(RandomForestClassifier(n_estimators=100))
classifiers.append(ExtraTreesClassifier(n_estimators=100))
classifiers.append(SGDClassifier(max_iter=10000))
classifiers.append(DecisionTreeClassifier())
classifiers.append(LogisticRegression(max_iter=10000,solver='lbfgs'))



import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
cv_results=[]
for classifier in classifiers:
    cv_results.append(cross_val_score(classifier,X_train,y_train,
                    scoring='accuracy',cv=kfold,n_jobs=1))


cv_means=[]
cv_std=[]
for cv_result in cv_results:
    cv_means.append(cv_result.mean())
    cv_std.append(cv_result.std())

cvResDf=pd.DataFrame({'cv_mean':cv_means,
                     'cv_std':cv_std,
                     'algorithm':['LinearSVC','RandomForest','ExtraTree','SGD','DecisionTree','LogisticRegression']})
cvResDf


sns.barplot(data=cvResDf,x='cv_mean',y='algorithm',**{'xerr':cv_std})



#kfold=StratifiedKFold(n_splits=2)
#RandomForestClassifier
RFC=RandomForestClassifier()
rf_param_grid={'n_estimators': [100, 300],
            'max_features': ['sqrt', 'auto', 'log2'],
            'max_depth': [None],
            'min_samples_split':[2,3,5],
            'min_samples_leaf':[1,3,10],
            'bootstrap':[False],
            'criterion':['gini']}
modelgsRFC = GridSearchCV(RFC,param_grid=rf_param_grid,cv=kfold,
                        scoring='accuracy',n_jobs=-1,verbose=1)
modelgsRFC.fit(X_train,y_train)
RFC_best=modelgsRFC.best_estimator_


ExtraTreesClassifier
ETC=ExtraTreesClassifier()

etc_param_grid={
        'n_estimators': [100,300],
        'max_features': ['sqrt', 'auto', 'log2'],
        'min_samples_leaf': [20,50,5],
       'min_samples_split': [15,36,5]}

modelgsETC = GridSearchCV(ETC,param_grid=etc_param_grid,cv=kfold,
                        scoring='accuracy',n_jobs=-1,verbose=1)
modelgsETC.fit(X_train,y_train)
ETC_best=modelgsETC.best_estimator_


DecisionTreeClassifier
DTC=DecisionTreeClassifier()
dtc_param_grid=[{'decisiontreeregressor__max_depth':depths,
              'decisiontreeregressor__min_samples_leaf':num_leafs}]
modelgsDTC = GridSearchCV(DTC,param_grid=dtc_param_grid,cv=kfold,
                        scoring='accuracy',n_jobs=-1,verbose=1)
modelgsDTC.fit(X_train,y_train)
DTC_best=modelgsDTC.best_estimator_



from sklearn.metrics import confusion_matrix
LR = LogisticRegression()
LSVC=LinearSVC(dual=False)
SGD=SGDClassifier()

LR = LR.fit(X_train, y_train)
LSVC = LSVC.fit(X_train, y_train)
SGD = SGD.fit(X_train, y_train)
RFC = RFC.fit(X_train, y_train)
ETC = RFC.fit(X_train, y_train)
DTC = RFC.fit(X_train, y_train)
LR_y=LR.predict(X_train).astype(int)
LSVC_y=LSVC.predict(X_train).astype(int)
SGD_y=SGD.predict(X_train).astype(int)
RFC_y=RFC.predict(X_train).astype(int)
ETC_y=ETC.predict(X_train).astype(int)
DTC_y=DTC.predict(X_train).astype(int)
print('LinearSVC confussion matrix\n',confusion_matrix(y_train.astype(int).astype(str),LSVC_y.astype(str)))
print('RandomForest confussion matrix\n',confusion_matrix(y_train.astype(int).astype(str),RFC_y.astype(str)))
print('ExtraTree confussion matrix\n',confusion_matrix(y_train.astype(int).astype(str),ETC_y.astype(str)))
print('SGD confussion matrix\n',confusion_matrix(y_train.astype(int).astype(str),SGD_y.astype(str)))
print('DecisionTree confussion matrix\n',confusion_matrix(y_train.astype(int).astype(str),DTC_y.astype(str)))
print('LogisticRegression confussion matrix\n',confusion_matrix(y_train.astype(int).astype(str),LR_y.astype(str)))



from sklearn.metrics import confusion_matrix

modelgsRFC_y=modelgsRFC.predict(X_train).astype(int)
modelgsETC_y=modelgsETC.predict(X_train).astype(int)
modelgsDTC_y=modelgsDTC.predict(X_train).astype(int)
print('RFC confussion matrix\n',confusion_matrix(y_train.astype(int).astype(str),modelgsRFC_y.astype(str)))
print('ETC confussion matrix\n',confusion_matrix(y_train.astype(int).astype(str),modelgsETC_y.astype(str)))
print('DTC confussion matrix\n',confusion_matrix(y_train.astype(int).astype(str),modelgsDTC_y.astype(str)))




#Model ensemble
modelVoting=VotingClassifier(estimators=[('RFC_best',RFC),('ETC_best',ETC),('DTC_best',DTC)],
                            voting='soft',n_jobs=-1,weights=[2,1,1])
modelVoting.fit(X_train,y_train)



print('the accuracy is %0.3f'%cross_val_score(modelVoting,X_train,y_train,
                                             scoring='accuracy',cv=kfold,n_jobs=-1,verbose=1).mean())
print('the AUC is %0.3f'%cross_val_score(modelVoting,X_train,y_train,
                                             scoring='roc_auc',cv=kfold,n_jobs=-1,verbose=1).mean())




#Model predict
modelVoting=VotingClassifier(estimators=[('RFC_best',RFC),('ETC_best',ETC),('DTC_best',DTC)],
                            voting='soft',n_jobs=-1,weights=[2,1,1])
modelVoting.fit(X_test,y_test)
print('the accuracy is %0.3f'%cross_val_score(modelVoting,X_test,y_test,
                                             scoring='accuracy',cv=kfold,n_jobs=-1,verbose=1).mean())
print('the AUC is %0.3f'%cross_val_score(modelVoting,X_test,y_test,
                                             scoring='roc_auc',cv=kfold,n_jobs=-1,verbose=1).mean())


# Save the model
from sklearn.externals import joblib
joblib.dump(modelVoting, 'StrPrice_model.pkl')
print("Model dumped!")

# Save the data columns from training
model_columns = list(X.columns)
joblib.dump(model_columns, 'model_columns.pkl')
print("Models columns dumped!")

# Save the scaler
joblib.dump(min_max_scaler, 'scaler.pkl')
print("scaler dumped!")
