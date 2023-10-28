import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.cluster import contingency_matrix
from math import *


CGM_FILE = "CGMData.csv"
INSULIN_DATA_FILE = "InsulinData.csv"

def cgm_input(cgm_file):
    cgm_cols = ['Index','Date','Time','Sensor Glucose (mg/dL)']
    cgm_df = pd.read_csv(cgm_file,sep=',',usecols=cgm_cols)
    cgm_df['TimeStamp'] = pd.to_datetime(cgm_df['Date'] + ' ' + cgm_df['Time'])
    cgm_df['CGM'] = cgm_df['Sensor Glucose (mg/dL)']
    cgm_df = cgm_df[['Index','TimeStamp','CGM','Date','Time']]
    cgm_df = cgm_df.sort_values(by=['TimeStamp'],ascending=True).fillna(method='ffill')
    cgm_df = cgm_df.drop(columns=['Date','Time','Index']).sort_values(by=['TimeStamp'],ascending=True)
    cgm_df = cgm_df[cgm_df['CGM'].notna()]
    cgm_df.reset_index(drop=True,inplace=True)
    return cgm_df

def insulin_input(insulin_file):
    ins_df = pd.read_csv(INSULIN_DATA_FILE,dtype='unicode')
    ins_df['TimeStamp'] = pd.to_datetime(ins_df['Date'] + ' ' + ins_df['Time'])
    ins_df = ins_df[['Date','Time','TimeStamp','BWZ Carb Input (grams)']]
    ins_df['ins'] = ins_df['BWZ Carb Input (grams)'].astype(float)
    ins_df = ins_df[(ins_df.ins != 0)]
    ins_df = ins_df[ins_df['ins'].notna()]
    ins_df = ins_df.drop(columns=['Date','Time','BWZ Carb Input (grams)']).sort_values(by=['TimeStamp'],ascending=True)
    ins_df.reset_index(drop=True,inplace=True)
    
    ins_df_shift = ins_df.shift(-1)
    ins_df = ins_df.join(ins_df_shift.rename(columns=lambda x : x + "_lag"))
    ins_df['total_mins_diff'] = (ins_df.TimeStamp_lag - ins_df.TimeStamp) / pd.Timedelta(minutes=1)
    ins_df['Patient'] = 'P1'
    
    ins_df.drop(ins_df[ins_df['total_mins_diff'] < 120].index,inplace=True)
    ins_df = ins_df[ins_df['ins_lag'].notna()]
    return ins_df

def cal_bins(ins_df):
    ins_values_df = ins_df['ins']
    max_ins_val = ins_values_df.max()
    min_ins_val = ins_values_df.min()
    num_bins = int((max_ins_val-min_ins_val)/20)
    
    ins_bin_labels = []
    for i in range(0,num_bins+1):
        ins_bin_labels.append(int(min_ins_val + i*20))
    return ins_bin_labels, num_bins, min_ins_val, max_ins_val
    
def cal_groundtruth(ins_df,len):
     bin_labels, num_bins, min_ins_val, max_ins_val = cal_bins(ins_df)
     ins_df['min_val'] = min_ins_val
     ins_df['bin'] = ((ins_df['ins']-ins_df['min_val'])/20).apply(np.ceil)
     bin_truth = pd.concat([len,ins_df],axis=1)
     bin_truth = bin_truth[bin_truth['len'].notna()]
     
     bin_truth.drop(bin_truth[bin_truth['len'] < 30].index,inplace=True)
     ins_df.reset_index(drop=True,inplace=True)
     return bin_truth
    
def cal_meal_time(ins_df, cgm_df):
    mealtime_df = []
    for i in ins_df.index:
        mealtime_df.append([ins_df['TimeStamp'][i] + pd.DateOffset(hours=-0.5),ins_df['TimeStamp'][i] + pd.DateOffset(hours=+2)])
        
    cgm_meal_df = []
    for  i in range(len(mealtime_df)):
        cgm_data = cgm_df.loc[(cgm_df['TimeStamp'] >= mealtime_df[i][0]) & (cgm_df['TimeStamp'] < mealtime_df[i][1])]['CGM']
        cgm_meal_df.append(cgm_data)
        
    ml_len_df = []
    mf_df = []
    for m in cgm_meal_df:
        sz = len(m)
        ml_len_df.append(sz)
        if sz == 30:
            mf_df.append(m)
    
    ml_length_df = pd.DataFrame(ml_len_df,columns=['len'])
    ml_length_df.reset_index(drop=True,inplace=True)
    
    return mf_df, ml_length_df
    
def get_bins(result_labels, true_labels):
    bin_result = {}
    bin_result[1], bin_result[2], bin_result[3], bin_result[4], bin_result[5], bin_result[6] = [], [], [], [], [], []
    for i in range(len(result_labels)):
        if result_labels[i] == 0:
            bin_result[1].append(i)
        elif result_labels[i] == 1:
            bin_result[2].append(i)
        elif result_labels[i] == 2:
            bin_result[3].append(i)
        elif result_labels[i] == 3:
            bin_result[4].append(i)
        elif result_labels[i] == 4:
            bin_result[5].append(i)
        elif result_labels[i] == 5:
            bin_result[6].append(i)

    bin_1, bin_2, bin_3, bin_4, bin_5, bin_6 = [], [], [], [], [], []

    for i in bin_result[1]:
        bin_1.append(true_labels[i])
    for i in bin_result[2]:
        bin_2.append(true_labels[i])
    for i in bin_result[2]:
        bin_3.append(true_labels[i])
    for i in bin_result[4]:
        bin_4.append(true_labels[i])
    for i in bin_result[5]:
        bin_5.append(true_labels[i])
    for i in bin_result[6]:
        bin_6.append(true_labels[i])
    total = len(bin_1) + len(bin_2) + len(bin_3) + len(bin_4) + len(bin_5) + len(bin_6)
    return total, bin_1, bin_2, bin_3, bin_4, bin_5, bin_6

def Cal_SSE(bin):
    SSE = 0
    if len(bin) != 0:
        avg = sum(bin) / len(bin)
        for i in bin:
            SSE += (i-avg) * (i-avg)
    return SSE

def main_entry():
    cgm_df = cgm_input(CGM_FILE)
    ins_df = insulin_input(INSULIN_DATA_FILE)
    meal_data, meal_len = cal_meal_time(ins_df,cgm_df)
    ground_truth_df = cal_groundtruth(ins_df,meal_len)
    
    feature_matrix = np.vstack((meal_data))
    
    feature_df = StandardScaler().fit_transform(feature_matrix)
    num_cluster = 6
    km = KMeans(n_clusters=num_cluster,random_state=0).fit(np.array(feature_df))
    ground_truth_bins = ground_truth_df['bin']
    
    true_labels = np.asarray(ground_truth_bins).flatten()
    for i in range(len(true_labels)):
        if isnan(true_labels[i]):
            true_labels[i] = 1
            
    km_labels = km.labels_
    for x in range(len(km_labels)):
        km_labels[x] = km_labels[x] + 1
        
    total, bin_1, bin_2, bin_3, bin_4, bin_5, bin_6 = get_bins(km_labels,true_labels)
    km_sse = (Cal_SSE(bin_1)*len(bin_1) + Cal_SSE(bin_2)*len(bin_2) + Cal_SSE(bin_3)*len(bin_3) + Cal_SSE(bin_4)*len(bin_4) + Cal_SSE(bin_5)*len(bin_5) + Cal_SSE(bin_6)*len(bin_6)) / total
    
    km_contingency = contingency_matrix(true_labels,km_labels)
    entropy, purity = [],[]
    for cluster in km_contingency:
        cluster = cluster / float(cluster.sum())
        e = 0
        for x in cluster:
            if x: 
                e = (cluster * [log(x,2)]).sum()
        p = cluster.max()
        entropy += [e]
        purity += [p]
        
    cluster_size = np.array([c.sum() for c in km_contingency])
    ratios = cluster_size / float(cluster_size.sum())
    km_entropy = (ratios * entropy).sum()
    km_purity = (ratios * purity).sum()
    
    
    feature_2 = []
    for i in feature_matrix:
        feature_2.append(i[1])
    
    feature_2 = np.array(feature_2)
    feature_2 = feature_2.reshape(-1,1)
    
    feature_dataset = StandardScaler().fit_transform(feature_2)
    dbscan = DBSCAN(eps=0.03,min_samples=8).fit(feature_dataset)
    
    dbscan_labels = dbscan.labels_
    total, bin_1, bin_2, bin_3, bin_4, bin_5, bin_6, = get_bins(dbscan_labels,true_labels)
    dbscan_sse = (Cal_SSE(bin_1)*len(bin_1) + Cal_SSE(bin_2)*len(bin_2) + Cal_SSE(bin_3)*len(bin_3) + Cal_SSE(bin_4)*len(bin_4) + Cal_SSE(bin_5)*len(bin_5) + Cal_SSE(bin_6)*len(bin_6)) / total
    
    dbscan_contingency = contingency_matrix(true_labels,dbscan_labels)
    entropy, purity = [],[]
    for cluster in dbscan_contingency:
        cluster = cluster / float(cluster.sum())
        e = 0
        for c in cluster:
            if c:
                e = (cluster * [log(c,2)]).sum()
        p = cluster.max()
        entropy += [e]
        purity += [p]
    
    cluster_size = np.array([c.sum() for c in dbscan_contingency])
    ratios = cluster_size / float(cluster_size.sum())
    dbscan_entropy = (ratios * entropy).sum()
    dbscan_purity = (ratios * purity).sum()
    result = []      
    result.append([km_sse,dbscan_sse,km_entropy,dbscan_entropy,km_purity,dbscan_purity])
    np.savetxt('./Result.csv',result,fmt="%f",delimiter=',')
    
    
if __name__ == '__main__':
    main_entry()