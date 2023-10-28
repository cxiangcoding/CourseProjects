"""
ASU CSE 272 Project 1: 
Author: Chunhua Xiang (cxiang4@asu.edu)
"""

import sklearn
import numpy as np
import pandas as pd

def get_cases(df,cnt):
    """
    get the six case values 
    """
    if ( cnt == 0 ):
        return np.zeros(6)
    
    data1 = len(df[df['CGM'] > 180].index) / cnt
    data2 = len(df[df['CGM'] > 250].index) / cnt
    data3 = len(df[(df['CGM'] >= 70) & (df['CGM'] <= 180)].index) / cnt
    data4 = len(df[(df['CGM'] >= 70) & (df['CGM'] <= 150)].index) / cnt
    data5 = len(df[df['CGM'] < 70].index) / cnt
    data6 = len(df[df['CGM'] < 54].index) / cnt
    res = np.array([data1,data2,data3,data4,data5,data6])
    return res

def get_avg_over_intevals(df, dates):
    """
    Analyze the DataFrame for average over intervals as specified in the project description
    df: is the corresponding DataFrame
    dates: is the unique dates that appear in df
    """
    data_list = []      # host mapping of each day and it's three intervals' data 
    for date in dates:
        day_data = {}
        midnight_ts = pd.Timestamp(date)
        morning_ts = pd.Timestamp(date + ' ' + '06:00:00')
        wholeday_df = df[df['Date'] == date]
        overnight_df = wholeday_df[wholeday_df['TimeStamp'] < morning_ts]
        daytime_df = wholeday_df[wholeday_df['TimeStamp'] >= morning_ts]
        day_data['wholeday'] = wholeday_df
        day_data['overnight'] = overnight_df
        day_data['daytime'] = daytime_df
        data_list.append(day_data)
    
    res = np.zeros(18)
    for day in data_list:
        sample_cnt = len(day['wholeday'])        # or use 288 
        res[:6] += get_cases(day['overnight'],288)
        res[6:12] += get_cases(day['daytime'],288)
        res[12:18] += get_cases(day['wholeday'],288)
    
    res /= len(data_list)
    return res
    
"""
The main entry function to call 
"""
def main():
    test_files = ["CGMData.csv", "InsulinData.csv"]  #Assume the test files are under the same directory 
    mode_change_mark = "AUTO MODE ACTIVE PLGM OFF"
    
    # Read in the two files as Data Frame
    pd.set_option('mode.chained_assignment', None)
    cgm_col_list = ['Index','Date','Time','Sensor Glucose (mg/dL)']
    cgm_df = pd.read_csv(test_files[0],usecols=cgm_col_list)
    cgm_df['TimeStamp'] = pd.to_datetime(cgm_df['Date'] + ' ' + cgm_df['Time'])
    cgm_df['CGM'] = cgm_df['Sensor Glucose (mg/dL)']
    cgm_df = cgm_df[['Index','TimeStamp','CGM','Date','Time']]
    cgm_df = cgm_df.replace('',np.nan)
    cgm_df = cgm_df.replace('NaN',np.nan)
    cgm_df = cgm_df[cgm_df['CGM'].notna()]
    #cgm_df = cgm_df.interpolate(inplace=True,method='ffill')
    
    # insulindata file handling
    insulin_df = pd.read_csv(test_files[1],parse_dates=[['Date','Time']],low_memory=False)
    
    # get the mode switch timestamp 
    mode_switch_ts = insulin_df.loc[insulin_df['Alarm']==mode_change_mark]['Date_Time'].min()
    #print(mode_switch_ts)
    
    # Separate the modes based on the timestamp for mannual (0) and auto (1)
    mode_dfs = [cgm_df.loc[cgm_df['TimeStamp'] < mode_switch_ts],cgm_df.loc[cgm_df['TimeStamp'] >= mode_switch_ts]]
    # Obtain the dates for mannual and auto
    manual_dates = mode_dfs[0]['Date'].unique()
    auto_dates = mode_dfs[1]['Date'].unique()

    
    #calculate first mannual and then auto
    result = np.zeros((2,18))
    result[0] = get_avg_over_intevals(mode_dfs[0],manual_dates)
    result[1] = get_avg_over_intevals(mode_dfs[1],auto_dates)
    result *= 100
    #result = np.around(result,2)
    output_df = pd.DataFrame(result)
    output_df.to_csv("Result.csv",header=False,index=False,index_label=False)
    
    return 
    
if __name__ == "__main__":
    main()