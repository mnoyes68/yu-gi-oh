import json
import zipfile
import pandas as pd
import datetime
import operator

# from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier

scaler = preprocessing.MinMaxScaler()

with zipfile.ZipFile("./small_training_data.json.zip", "r") as z:
    dfx = pd.read_json(z.open('small_training_data.json'), orient='columns')
    dfy = pd.read_csv('small_training_results.csv', sep=',')
    X = scaler.fit_transform(dfx)
    #X = dfx.values
    y = dfy.values[:,1]
    #clf = LogisticRegression(random_state=0, C=2.0, solver='sag').fit(X, y)
    #clf = svm.SVC(C=35, probability=True)
    clf = RandomForestClassifier(n_estimators=500, min_samples_split=5, max_depth=30)
    clf.fit(X, y)

with zipfile.ZipFile("./small_test_data.json.zip", "r") as z:
    dfx = pd.read_json(z.open('small_test_data.json'), orient='columns')
    dfy = pd.read_csv('small_test_results.csv', sep=',')
    X = scaler.fit_transform(dfx)
    #X = dfx.values
    y = dfy.values[:,1]
    print "Predict"
    print clf.predict(X[:12, :])
    print "Predict Probability"
    print clf.predict_proba(X[:12, :]) 
    print "Score"
    print clf.score(X, y)



'''
    print clf.coef_
    coeff = {}
    for i in range(0, 59):
        coeff[list(dfx)[i]] = clf.coef_[:, i][0]
    sorted_coeff = sorted(coeff.items(), key=operator.itemgetter(1))
    for c in sorted_coeff:
        print c
'''

'''
print datetime.datetime.now()
df = pd.read_json('small_training_data.json', orient='columns')
print len(df)

for i in range(0, len(X)):
    state = X[i:i+1,:]
    result = y[i]
    prediction = clf.predict(state)[0]
    if prediction == result:
        correct += 1
    total += 1
test_grade = correct / float(total)

X, y = load_iris(return_X_y=True)
clf = LogisticRegression(random_state=0, solver='lbfgs', multi_class='multinomial').fit(X, y)
print "Predict", str(X[:2, :])
print clf.predict(X[:2, :])
print "Predict Probability", str(X[:2, :])
print clf.predict_proba(X[:2, :]) 
print "Score"
print clf.score(X, y)
'''

