#!/usr/bin/env python
# coding: utf-8

# In[4]:


from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier
from sklearn.svm import LinearSVC
from sklearn import metrics
from sklearn.model_selection import GridSearchCV,cross_val_score,StratifiedKFold
from sklearn.ensemble import VotingClassifier
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
from sklearn.externals import joblib
import pickle
from sklearn import preprocessing
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

#The data pass through need has 6 attributes:product, buyingParty, sellingParty, quantity, strikePrice, errorneous
def compute_strike_price_model(data):
    data = handle_non_numerical_data(data)
    scalers=joblib.load(os.path.join(CURRENT_DIR, "scaler.pkl"))
    X=scalers.transform(data)
    X =data.iloc[:,:5]
    y =data.iloc[:,5]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True, random_state = 0)
    RFC=RandomForestClassifier(n_estimators=200,min_samples_leaf=5, min_samples_split=5,)
    ETC=ExtraTreesClassifier(n_estimators=200)
    DTC=DecisionTreeClassifier()
    kfold=StratifiedKFold(n_splits=10)
    
    RFC = RFC.fit(X_train, y_train)
    ETC = RFC.fit(X_train, y_train)
    DTC = RFC.fit(X_train, y_train)
    #Model ensemble
    modelVoting=VotingClassifier(estimators=[('RFC_best',RFC),('ETC_best',ETC),('DTC_best',DTC)],
                            voting='soft',n_jobs=-1,weights=[2,1,1])
    modelVoting.fit(X_train,y_train)
    score = cross_val_score(modelVoting,X_test,y_test,
                                             scoring='accuracy',cv=kfold,n_jobs=-1,verbose=1).mean()
    joblib.dump(modelVoting, 'StrPrice_model.pkl')
 
    # some time later...
 
    # load the model from disk
    pickled_model=joblib.load('StrPrice_model.pkl')    
    return (score, pickled_model)


# In[ ]:




