import json
import zipfile
import pandas as pd
import datetime
import operator

# from sklearn.datasets import load_iris
from sklearn import preprocessing

from keras.models import Sequential
from keras.layers import Activation
from keras.layers import BatchNormalization
from keras.layers import Dense
from keras import regularizers

scaler = preprocessing.MinMaxScaler()
print datetime.datetime.now()
with zipfile.ZipFile("./training_data.json.zip", "r") as z:
    dfx = pd.read_json(z.open('training_data.json'), orient='columns')
    dfy = pd.read_csv('training_results.csv', sep=',')
    X = scaler.fit_transform(dfx)
    #X = dfx.values
    y = dfy.values[:,1]
    model = Sequential()
    model.add(Dense(100, input_dim=59, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(50, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(1, activation="sigmoid"))
    model.compile(optimizer='rmsprop',
              loss='binary_crossentropy',
              metrics=['accuracy'])
    model.fit(X, y, epochs=10, batch_size=512)

with zipfile.ZipFile("./test_data.json.zip", "r") as z:
    dfx = pd.read_json(z.open('test_data.json'), orient='columns')
    dfy = pd.read_csv('test_results.csv', sep=',')
    X = scaler.fit_transform(dfx)
    #X = dfx.values
    y = dfy.values[:,1]
    score = model.evaluate(X, y, batch_size=512)
    print "Score"
    print score

print datetime.datetime.now()


