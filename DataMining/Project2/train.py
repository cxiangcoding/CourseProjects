"""
This program reads in insulin and CGM data and extract meal and no-meal data respetively. 
It then extracts features from those two datasets and generates a train model. 
"""
from datetime import timedelta
from joblib import dump, load
import numpy as np
import pandas as pd
from scipy.fftpack import fft, ifft, rfft
from sklearn.utils import shuffle
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import KFold, RepeatedKFold
#from sklearn.metrics import classification_report
#from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
import pickle

def read_data():
    insulin_data1 = pd.read_csv('InsulinData.csv', low_memory=False, usecols=['Date', 'Time', 'BWZ Carb Input (grams)'])
    insulin_data1['date_time_stamp'] = pd.to_datetime(insulin_data1['Date'] + ' ' + insulin_data1['Time'])
    insulin_data2 = pd.read_csv('Insulin_patient2.csv', low_memory=False, usecols=['Date', 'Time', 'BWZ Carb Input (grams)'])
    insulin_data2['date_time_stamp'] = pd.to_datetime(insulin_data2['Date'] + ' ' + insulin_data2['Time'])
    cgm_data1 = pd.read_csv('CGMData.csv', low_memory=False, usecols=['Date', 'Time', 'Sensor Glucose (mg/dL)'])
    cgm_data1['date_time_stamp'] = pd.to_datetime(cgm_data1['Date'] + ' ' + cgm_data1['Time'])
    cgm_data2 = pd.read_csv('CGM_patient2.csv', low_memory=False, usecols=['Date', 'Time', 'Sensor Glucose (mg/dL)'])
    cgm_data2['date_time_stamp'] = pd.to_datetime(cgm_data2['Date'] + ' ' + cgm_data2['Time'])
    return insulin_data1, insulin_data2, cgm_data1, cgm_data2


def extract_meal_data(insulin_data, cgm_data, date_identifier):
    insulin_data_copy = insulin_data.copy()
    insulin_data_copy = insulin_data_copy.set_index('date_time_stamp')
    insulin_data_cleaned = insulin_data_copy.sort_values(by='date_time_stamp', ascending=True).dropna().reset_index()
    insulin_data_cleaned['BWZ Carb Input (grams)'].replace(0.0, np.nan, inplace=True)
    insulin_data_cleaned = insulin_data_cleaned.dropna()
    insulin_data_cleaned = insulin_data_cleaned.reset_index().drop(columns='index')
    valid_meal_timestamps_list = []
    for index, i in enumerate(insulin_data_cleaned['date_time_stamp']):
        try:
            value = (
                insulin_data_cleaned['date_time_stamp'][index+1]-i).seconds / 60.0
            if value >= 120:
                valid_meal_timestamps_list.append(i)
        except KeyError:
            break
    meal_data_list = []

    if date_identifier == 1:
        date_format = '%-m/%-d/%Y'
        time_format = '%-H:%-M:%-S'
    elif date_identifier == 2:
        date_format = '%Y-%m-%d'
        time_format = '%H:%M:%S'
    else:
        raise ValueError('Invalid date identifier')

    for index, date_time in enumerate(valid_meal_timestamps_list):
        start = pd.to_datetime(i - timedelta(minutes=30))
        end = pd.to_datetime(i + timedelta(minutes=90))
        get_date = date_time.date().strftime(date_format)
        meal_data_list.append(cgm_data.loc[cgm_data['Date'] == get_date].set_index('date_time_stamp').between_time(start_time=start.strftime(time_format), end_time=end.strftime(time_format))['Sensor Glucose (mg/dL)'].values.tolist())
    return pd.DataFrame(meal_data_list)


def extract_no_meal_data(insulin_data, cgm_data):
    insulin_data_copy = insulin_data.copy()
    insulin_data_cleaned = insulin_data_copy.sort_values(by='date_time_stamp', ascending=True).replace(0.0, np.nan).dropna().copy()
    insulin_data_cleaned = insulin_data_cleaned.reset_index().drop(columns='index')
    valid_no_meal_timestamps_list = []
    for idx, i in enumerate(insulin_data_cleaned['date_time_stamp']):
        try:
            value = (
                insulin_data_cleaned['date_time_stamp'][idx + 1]-i).seconds // 3600
            if value >= 4:
                valid_no_meal_timestamps_list.append(i)
        except KeyError:
            break

    no_meal_data_list = []
    for idx, i in enumerate(valid_no_meal_timestamps_list):
        counter = 1
        try:
            len_of_dataset = len(cgm_data.loc[(cgm_data['date_time_stamp'] >= valid_no_meal_timestamps_list[idx]+pd.Timedelta(hours=2)) & (cgm_data['date_time_stamp'] < valid_no_meal_timestamps_list[idx+1])])//24
            while (counter <= len_of_dataset):
                if counter == 1:
                    no_meal_data_list.append(cgm_data.loc[(cgm_data['date_time_stamp'] >= valid_no_meal_timestamps_list[idx]+pd.Timedelta(hours=2)) & (cgm_data['date_time_stamp'] < valid_no_meal_timestamps_list[idx+1])]['Sensor Glucose (mg/dL)'][:counter*24].values.tolist())
                else:
                    no_meal_data_list.append(cgm_data.loc[(cgm_data['date_time_stamp'] >= valid_no_meal_timestamps_list[idx]+pd.Timedelta(hours=2)) & (
                        cgm_data['date_time_stamp'] < valid_no_meal_timestamps_list[idx+1])]['Sensor Glucose (mg/dL)'][(counter-1)*24:(counter)*24].values.tolist())
                counter += 1
        except IndexError:
            break
    return pd.DataFrame(no_meal_data_list)

def clean_data(data):
    index_to_drop = data.isna().sum(axis=1).replace(0, np.nan).dropna().where(lambda x: x > 6).dropna().index
    data_cleaned = data.drop(data.index[index_to_drop]).reset_index().drop(columns='index')
    data_cleaned = data_cleaned.interpolate(method='linear', axis=1)
    index_to_drop_again = data_cleaned.isna().sum(axis=1).replace(0, np.nan).dropna().index
    data_cleaned = data_cleaned.drop(data.index[index_to_drop_again]).reset_index().drop(columns='index')
    data_cleaned['tau_time'] = (data_cleaned.iloc[:, 22:25].idxmin(axis=1)-data_cleaned.iloc[:, 5:19].idxmax(axis=1))*5
    data_cleaned['difference_in_glucose_normalized'] = (data_cleaned.iloc[:, 5:19].max(axis=1)-data_cleaned.iloc[:, 22:25].min(axis=1))/(data_cleaned.iloc[:, 22:25].min(axis=1))
    data_cleaned = data_cleaned.dropna().reset_index().drop(columns='index')
    return data_cleaned

def extract_meal_feature_matrix(meal_data):
    meal_cleaned_data = clean_data(meal_data)
    first_max_power = []
    first_max_index = []
    second_max_power = []
    second_max_index = []
    for i in range(len(meal_cleaned_data)):
        array = abs(rfft(meal_cleaned_data.iloc[:, 0:30].iloc[i].values.tolist())).tolist()
        sorted_array = abs(rfft(meal_cleaned_data.iloc[:, 0:30].iloc[i].values.tolist())).tolist()
        sorted_array.sort()
        first_max_power.append(sorted_array[-2])
        second_max_power.append(sorted_array[-3])
        first_max_index.append(array.index(sorted_array[-2]))
        second_max_index.append(array.index(sorted_array[-3]))
        
    meal_feature_matrix = pd.DataFrame()
    meal_feature_matrix['tau_time'] = meal_cleaned_data['tau_time']
    meal_feature_matrix['difference_in_glucose_normalized'] = meal_cleaned_data['difference_in_glucose_normalized']
    meal_feature_matrix['first_max_power'] = first_max_power
    meal_feature_matrix['second_max_power'] = second_max_power
    meal_feature_matrix['first_max_index'] = first_max_index
    meal_feature_matrix['second_max_index'] = second_max_index

    tm = meal_cleaned_data.iloc[:, 22:25].idxmin(axis=1)
    maximum = meal_cleaned_data.iloc[:, 5:19].idxmax(axis=1)

    data_list = []
    second_differential_data = []
    standard_deviation = []

    for i in range(len(meal_cleaned_data)):
        data_list.append(np.diff(meal_cleaned_data.iloc[:, maximum[i]:tm[i]].iloc[i].tolist()).max())
        second_differential_data.append(np.diff(np.diff(meal_cleaned_data.iloc[:, maximum[i]:tm[i]].iloc[i].tolist())).max())
        standard_deviation.append(np.std(meal_cleaned_data.iloc[i]))
    meal_feature_matrix['2ndDifferential'] = second_differential_data
    meal_feature_matrix['standard_deviation'] = standard_deviation
    return meal_feature_matrix

def extract_no_meal_feature_matrix(no_meal_data):
    no_meal_cleaned_data = clean_data(no_meal_data)
    no_meal_feature_matrix = pd.DataFrame()

    first_max_power = []
    first_max_index = []
    second_max_power = []
    second_max_index = []
    for i in range(len(no_meal_cleaned_data)):
        array = abs(rfft(no_meal_cleaned_data.iloc[:, 0:24].iloc[i].values.tolist())).tolist()
        sorted_array = abs(rfft(no_meal_cleaned_data.iloc[:, 0:24].iloc[i].values.tolist())).tolist()
        sorted_array.sort()
        first_max_power.append(sorted_array[-2])
        second_max_power.append(sorted_array[-3])
        first_max_index.append(array.index(sorted_array[-2]))
        second_max_index.append(array.index(sorted_array[-3]))
    no_meal_feature_matrix['tau_time'] = no_meal_cleaned_data['tau_time']
    no_meal_feature_matrix['difference_in_glucose_normalized'] = no_meal_cleaned_data['difference_in_glucose_normalized']
    no_meal_feature_matrix['first_max_power'] = first_max_power
    no_meal_feature_matrix['second_max_power'] = second_max_power
    no_meal_feature_matrix['first_max_index'] = first_max_index
    no_meal_feature_matrix['second_max_index'] = second_max_index
    first_differential_data = []
    second_differential_data = []
    standard_deviation = []
    for i in range(len(no_meal_cleaned_data)):
        first_differential_data.append(np.diff(no_meal_cleaned_data.iloc[:, 0:24].iloc[i].tolist()).max())
        second_differential_data.append(np.diff(np.diff(no_meal_cleaned_data.iloc[:, 0:24].iloc[i].tolist())).max())
        standard_deviation.append(np.std(no_meal_cleaned_data.iloc[i]))
    no_meal_feature_matrix['2ndDifferential'] = second_differential_data
    no_meal_feature_matrix['standard_deviation'] = standard_deviation
    return no_meal_feature_matrix


insulin_data1, insulin_data2, cgm_data1, cgm_data2 = read_data()

meal_data1 = extract_meal_data(insulin_data1, cgm_data1, 1)
meal_data2 = extract_meal_data(insulin_data2, cgm_data2, 2)

meal_data1 = meal_data1.iloc[:, 0:30]
meal_data2 = meal_data2.iloc[:, 0:30]

no_meal_data1 = extract_no_meal_data(insulin_data1, cgm_data1)
no_meal_data2 = extract_no_meal_data(insulin_data2, cgm_data2)

meal_feature_matrix1 = extract_meal_feature_matrix(meal_data1)
meal_feature_matrix2 = extract_meal_feature_matrix(meal_data2)

meal_feature_matrix = pd.concat([meal_feature_matrix1, meal_feature_matrix2]).reset_index().drop(columns='index')

no_meal_feature_matrix = extract_no_meal_feature_matrix(no_meal_data1)
no_meal_feature_matrix2 = extract_no_meal_feature_matrix(no_meal_data2)

no_meal_feature_matrix = pd.concat([no_meal_feature_matrix, no_meal_feature_matrix2]).reset_index().drop(columns='index')

meal_feature_matrix['label'] = 1

no_meal_feature_matrix['label'] = 0
total_data = pd.concat([meal_feature_matrix, no_meal_feature_matrix]).reset_index().drop(columns='index')

dataset = shuffle(total_data, random_state=1).reset_index().drop(columns='index')
kfold = KFold(n_splits=10, shuffle=False)

# Separate the features from the labels and train a decision tree classifier
principaldata = dataset.drop(columns='label')
scores_rf = []
model = DecisionTreeClassifier(criterion="entropy")
for train_index, test_index in kfold.split(principaldata):
    x_train, x_test, y_train, y_test = principaldata.loc[train_index], principaldata.loc[test_index], dataset.label.loc[train_index], dataset.label.loc[test_index]
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    scores_rf.append(model.score(x_test, y_test))
#print('Prediction Score is : ', np.mean(scores_rf) * 100)

# Train the classifier on the entire dataset and save it to a file
classifier = DecisionTreeClassifier(criterion="entropy")
x, y = principaldata, dataset['label']
classifier.fit(x, y)
dump(classifier, 'DecisionTreeClassifier.pickle')
