import re
import os
from typing import Literal
import pandas as pd

def read_logs(data_path) -> tuple[list[str], list[str]]:  
    # get all subdirectories in data folder
    dataset_labels = []
    for dir in os.scandir(data_path):
        dataset_labels.append(dir.name)

    # get all log files for each data set
    dataset_logs = []
    log_pattern = r'[A-Za-z0-9]*.log'
    for i, dir_list in enumerate([os.listdir(data_path + '/' + dir) for dir in dataset_labels]):
        specific_log_title = []
        specific_log = [] 
        for file in dir_list:
            if re.search(log_pattern, file):
                specific_log_title.append(file)
                f = open(data_path + '/' + dataset_labels[i] + '/' + file)
                specific_log.append(f.read())
                f.close()
        dataset_logs.append((specific_log_title,specific_log))
    print(f'Successfully found the following labels : {dataset_labels}')
    print(f'And found {len(dataset_logs[0][0])} logs for the {dataset_labels[0]} label')
    data = (dataset_labels, dataset_logs)

    return data


def split_logs(log) -> tuple[list[str], list[str]]:

    split_logs = str(log).split(r'end of world_state')
    split_logs = split_logs[:-1]

    for i, log in enumerate(split_logs):
        split_logs[i] = log.split('end of events')[0]
    
    flight_envelopes = [] # contains all timestep data
    events = [] # contains the events at the end of each log file
    for i, log in enumerate(split_logs):
        flight_envelopes.append(log.split('events')[0])
        events.append(log.split('events')[1])

    return (flight_envelopes, events)

def merge_logs_into_dataframes(flight_envelopes, events):
    flight_dfs = []
    for envelope in flight_envelopes: 
        df_arrays = []
        for i in envelope.split(r'\n'):
            df_arrays.append(i.split(','))
        flight_df = pd.DataFrame(df_arrays)
        flight_df = clean_flight_df(flight_df)
        flight_dfs.append(flight_df)
    print(f"Successfully merged {len(flight_dfs)} flight envelope logs into DataFrames!")
    
    
    # need to merge events df
    
    
    return (flight_dfs, event_dfs)

def clean_flight_df(flight_df):

    flight_df.columns = [re.search(r'([A-Za-z0-9(/)]*):', s).group(0) for s in df.iloc[0,:]]
    flight_df = flight_df[flight_df['x:'].notnull()]
    flight_df = flight_df.applymap(lambda x: re.sub(sub_pattern, '', x))
    return flight_df
