import pandas as pd
import csv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
import requests

ml_df=pd.read_csv('Resources/ml_modeled.csv', sep=',')
ml_df=ml_df.drop('Index', axis=1)
dummy_df=pd.get_dummies(ml_df)
X=dummy_df.drop('median_sale_price', axis=1)
y=dummy_df['median_sale_price'].round(-5)
y.value_counts()
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)
scaler = StandardScaler().fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)
clf = RandomForestClassifier(random_state=41, n_estimators=100).fit(X_train_scaled, y_train)
pickle.dump(clf, open('model.pkl','wb'))

model=pickle.load(open('model.pkl','rb'))
test=[[20223,6,10,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]]
print(model.predict(test))

