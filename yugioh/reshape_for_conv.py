import json
import zipfile
import pandas as pd
import datetime
import operator
import numpy as np
from pandas.io.json import json_normalize

# from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier

scaler = preprocessing.MinMaxScaler()
#object_props = ['OpponentMonster1', 'OpponentMonster2', 'OpponentMonster3', 'OpponentMonster4', 'OpponentMonster5', 'PlayerMonster1', 'PlayerMonster2', 'PlayerMonster3', 'PlayerMonster4', 'PlayerMonster5']
object_props = ['OpponentMonster1', 'OpponentMonster2', 'OpponentMonster3', 'OpponentMonster4', 'OpponentMonster5', 'PlayerMonster1', 'PlayerMonster2', 'PlayerMonster3', 'PlayerMonster4', 'PlayerMonster5']


with zipfile.ZipFile("./conv_training_data.json.zip", "r") as z:
    #pd.read_json(z.open('conv_training_data.json'), orient='columns')
    data = json.load(z.open('conv_training_data.json'))
    df = json_normalize(data)
    print df.head()


    '''
    pm1_col = [col for col in df if col.startswith('PlayerMonster1')]
    pm2_col = [col for col in df if col.startswith('PlayerMonster2')]
    pm3_col = [col for col in df if col.startswith('PlayerMonster3')]
    pm4_col = [col for col in df if col.startswith('PlayerMonster4')]
    pm5_col = [col for col in df if col.startswith('PlayerMonster5')]
    om1_col = [col for col in df if col.startswith('OpponentMonster1')]
    om2_col = [col for col in df if col.startswith('OpponentMonster2')]
    om3_col = [col for col in df if col.startswith('OpponentMonster3')]
    om4_col = [col for col in df if col.startswith('OpponentMonster4')]
    om5_col = [col for col in df if col.startswith('OpponentMonster5')]

    pm1df = df[pm1_col]
    pm2df = df[pm2_col]
    pm3df = df[pm3_col]
    pm4df = df[pm4_col]
    pm5df = df[pm5_col]
    om1df = df[om1_col]
    om2df = df[om2_col]
    om3df = df[om3_col]
    om4df = df[om4_col]
    om5df = df[om5_col]

    for i in range(0, len(df)):
        xlist = [[pm1df.values[i,:].tolist(), om1df.values[i,:].tolist()], [pm2df.values[i,:].tolist(), om2df.values[i,:].tolist()], [pm3df.values[i,:].tolist(), om3df.values[i,:].tolist()], [pm4df.values[i,:].tolist(), om4df.values[i,:].tolist()], [pm5df.values[i,:].tolist(), om5df.values[i,:].tolist()]]
        X = np.asarray(xlist)
        print X
        #print type(X)
        #print X.shape
    '''

    '''
    dfx = pd.read_json(z.open('conv_training_data.json'), orient='columns')
    dfy = pd.read_csv('conv_training_results.csv', sep=',')
    objdfx = dfx[object_props]
    metadfx = dfx.drop(object_props, axis=1)
    X = objdfx.values
    print objdfx.info()
    '''

    #X = scaler.fit_transform(dfx)
    #X = dfx.values
    #y = dfy.values[:,1]
    #print dfx
    #print dfx.dtypes
    #print dfx.columns
    #print dfx.OppLP
    #print len(dfx)
    #print dfx['OppLP']
    #objdfx = dfx[object_props]
    #metadfx = dfx.drop(object_props, axis=1)

    #print objdfx
    #print objdfx.columns
    #print metadfx
    #print metadfx.columns
    #print dfx.index
    #print dfx


    #clf = LogisticRegression(random_state=0, C=2.0, solver='sag').fit(X, y)
    #clf = svm.SVC(C=35, probability=True)

    #clf = RandomForestClassifier(n_estimators=500, min_samples_split=5, max_depth=30)
    #clf.fit(X, y)