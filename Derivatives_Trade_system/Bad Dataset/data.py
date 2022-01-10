# coding: utf-8
import pandas as pd
from pandas import DataFrame
import random
import string
import numpy as np

df = pd.read_csv("/Users/feng/Downloads/cs261dummydata/derivativeTrades/2016/April/02042016.csv")
L1 = random.sample(range(df.iloc[:,0].size), 500)
for i in L1:
    a = np.random.choice(list(string.ascii_lowercase))
    name = df.loc[i,"product"]
    name = name[:2] + a +name[3:]
    df.loc[i,"product"]=[name]
    
L2 = random.sample(range(df.iloc[:,0].size),800)
for j in L2:
    iD = df.loc[j,["buyingParty"]]
    iD = list(list(iD)[0])
    iD1 = "".join(iD)
    df.loc[j,"buyingParty"]=[iD1.replace(iD1[5],str(random.randint(1,9)))]

L3 = random.sample(range(df.iloc[:,0].size),800)
for k in L3:
    b_iD = df.loc[k,["sellingParty"]]
    b_iD = list(list(b_iD)[0])
    iD2 = "".join(b_iD)
    df.loc[k,"sellingParty"]=[iD2.replace(iD2[4],str(random.randint(1,9)))]

L4 = random.sample(range(df.iloc[:,0].size),800)
for l in L4:
    price = df.loc[l,["underlyingPrice"]]*5
    amount = price*df.loc[l,"quantity"]
    df.loc[l,"underlyingPrice"]=[list(price)[0]]
    df.loc[l,"notionalAmount"]=[list(amount)[0]]

df.to_csv("/Users/feng/Desktop/bad_dataset3.csv",index=None)

