import re
import os
from typing import Literal
import pandas as pd
from tqdm import tqdm
import numpy as np
import warnings
from itertools import compress

warnings.simplefilter(action='ignore', category=FutureWarning)

def read_logs(data_path: str) -> tuple[list[str], list[str]]:
    # returns maneuvers (directory names) and all their associated log files as tuple of lists

    # get all subdirectories in data folder
    dataset_labels = []
    for dir in os.scandir(data_path):
        dataset_labels.append(dir.name)

    # get all log files for each data set
    dataset_log_titles = []
    log_pattern = r'[A-Za-z0-9]*.log'
    for i, dir_list in enumerate([os.listdir(data_path + '/' + dir) for dir in dataset_labels]):
        specific_log_title = []
        for file in dir_list:
            if re.search(log_pattern, file):
                specific_log_title.append(file)
                #f = open(data_path + '/' + dataset_labels[i] + '/' + file)
                #specific_log.append(f.read())
                #f.close()
        dataset_log_titles.append(specific_log_title)
    print(f'Successfully found the following labels : {dataset_labels}')
    for i, label in enumerate(dataset_labels):
        print(f'Found {len(dataset_log_titles[i])} logs for the "{label}" label')
    

    return dataset_labels, dataset_log_titles

def read_log_file_contents(folder: str, filename: str, file_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    # returns a tuple of dataframes (timestep data, debrief data) for a given maneuver-log permutation

    # new dataframe
    df = pd.DataFrame(columns=['CATEGORY', 'RUN_ID', 'TIME', 'ALT', 'SPEED', 'PITCH', 'BANK', 'RWR', 'GT_MISSILE_DIST', 'T_UNTIL_IMPACT'])
    event_df = pd.DataFrame(columns=['CATEGORY','RUN_ID','IMPACT_TIME'])
    # open the file
    with open(file_path, 'r') as f:
        # if line starts with "Player", then parse the line
        text = f.readlines()
        f.close()
    
    for i, line in enumerate(text):
        if line.startswith('Player'):
            # new dict for each line
            line_dict = {}

            # category is the folder name
            line_dict['CATEGORY'] = folder

            # run_id is the filename
            line_dict['RUN_ID'] = filename

            # regex to strip excess info and split string into list
            # here 
            sub_pattern = r'["[\' \sA-Za-z0-9(/)]*:'
            line_info = re.sub(sub_pattern,'',line)
            line_info = line_info.split(',')
            
            # line_info indices: 
            # t: 0, MSLAlt: 1, speed(m/s): 2, heading: 3, x: 4, y: 5, z: 6, pitch: 7, bank: 8, yaw/emitters: 9 
            line_dict['TIME'] = line_info[0]
            line_dict['ALT'] = line_info[1]
            line_dict['SPEED'] = line_info[2]
            line_dict['PITCH'] = line_info[7]
            line_dict['BANK'] = line_info[8]
            line_dict['RWR'] = line.split('Emitters.')[1]

            line_dict['T_UNTIL_IMPACT'] = np.nan # place holder
            
            # if nextline doesn't start with "sam", GT_MISSILE_DIST is infinite
            # df.shift(i, 2)
            if i + 1 <= len(text)-1:
                if not text[i+1].startswith('Sam'):
                    # GT_MISSILE_DIST is infinite
                    line_dict['GT_MISSILE_DIST'] = np.inf

                else:
                    # Calculate GT_MISSILE_DIST from X, Y Z of aircraft and missile
                    # x, y, z of aircraft
                    ac_X = float(line_info[4])
                    ac_Y = float(line_info[5])
                    ac_Z = float(line_info[6])

                    # X, Y, Z of missile
                    sam_X = float(text[i+1].split('x: ')[1].split(' ')[0])
                    sam_Y = float(text[i+1].split('y: ')[1].split(' ')[0])
                    sam_Z = float(text[i+1].split('z: ')[1].split(' ')[0])

                    # calculate distance
                    line_dict['GT_MISSILE_DIST'] = np.sqrt((ac_X - sam_X)**2 + (ac_Y - sam_Y)**2 + (ac_Z - sam_Z)**2)
        
            # append the line to the dataframe
            df = df.append(line_dict, ignore_index=True)
        elif line.startswith('\t\ttype\t=\t"hit"'):
            
            event_dict = {}
            
            # category is the folder name
            event_dict['CATEGORY'] = folder

            # run_id is the filename
            event_dict['RUN_ID'] = filename
            
            # impact_time is the t = value in the debrief section of the log file, it comes 3 rows after the 'hit' message
            time_row = text[i+3]
            event_dict['IMPACT_TIME'] = float(re.sub(r'[\st=,]*', '', time_row))
            event_df = event_df.append(event_dict, ignore_index=True)

    #return df
    return (df, event_df)


def drop_clean_runs(dataset_dfs: list[pd.DataFrame], dataset_event_dfs: list[pd.DataFrame]) -> tuple[list[pd.DataFrame], list[pd.DataFrame]]:
    # returns two lists of dataframes where empty dataframes have been dropped from both lists at the same indices

    # create a mask checking for clean runs via event logs
    mask = np.invert(np.array([event_df.empty for event_df in dataset_event_dfs])) # removed an index of [0] on dataset_dfs
    
    # mask over dataset
    dataset_dfs = list(compress(dataset_dfs,mask)) # removed an index of [0] on dataset_dfs
    
    dataset_event_dfs = list(compress(dataset_event_dfs,mask)) # removed an index of [0] on dataset_dfs
    
    return dataset_dfs, dataset_event_dfs

def t_until_impact(row: pd.Series, impact: float) -> pd.Series:
    # adds a column for the time until impact (passed as argument 'impact')
    row['T_UNTIL_IMPACT'] = impact - float(row['TIME'])
    
    return row


def find_first_RWR_lock(col: pd.Series) -> int:
    # returns the index of the first RWR lock detection, used for indexing the df.loc[first_lock, t]
    indices = []
    for i, r in enumerate(col):
        search = re.search(r'.*(missile_radio_guided Mode:)', r)
        if search is not None:
            indices.append(i)
    first_lock_index = int(indices[0])
    return first_lock_index  


def time_since_lock_on(row: pd.Series, first_lock_t: float) -> pd.Series:
    # adds a column to the dataframe for time since the RWR first detected a lock (passed as argument 'first_lock_t')
    
    row['TIME_SINCE_LOCK'] = float(row['TIME']) - float(first_lock_t)
    return row

def drop_early_and_late_runs(df: pd.DataFrame) -> pd.DataFrame:
    # removes data from before the lock and after the missile hit
    df = df[df['T_UNTIL_IMPACT'] > 0]
    df = df[df['TIME_SINCE_LOCK'] > 0]
    return df

### following code is not in use ###

# this is all massively more efficient than the above method of generating dfs, ~10% of the computation required
# but good luck getting it to pipe through all the data

# def split_logs(log) -> tuple[list[str], list[str]]:

#     split_logs = str(log).split(r'end of world_state')
#     split_logs = split_logs[:-1]

#     for i, log in enumerate(split_logs):
#         split_logs[i] = log.split('end of events')[0]
    
#     print(f"Separating flight envelopes and events for {len(split_logs)} logs")
#     flight_envelopes = [] # contains all timestep data
#     events = [] # contains the events at the end of each log file
#     for i, log in enumerate(split_logs):
#         flight_envelopes.append(log.split('events')[0])
#         events.append(log.split('events')[1])

#     return (flight_envelopes, events)

# def merge_logs_into_dataframes(flight_envelopes):
    
#     flight_dfs = []
#     for envelope in flight_envelopes: 
#         df_arrays = []
#         for i in envelope.split(r'\n'):
#             df_arrays.append(i.split(','))
#         flight_df = pd.DataFrame(df_arrays)
#         flight_df, sam_df = clean_flight_df(flight_df)
        
#         flight_dfs.append(flight_df)
#     #print(f"Successfully merged {len(flight_dfs)} flight envelope logs into DataFrames!")
    
    
#     # need to merge events df
#     event_dfs = pd.DataFrame()
    
#     return (flight_dfs, sam_df, event_dfs)

# def clean_flight_df(flight_df) -> tuple[pd.DataFrame, pd.DataFrame]:
    
#     flight_df.columns = [re.search(r'([A-Za-z0-9(/)]*):', s).group(0) for s in flight_df.iloc[0,:]]
    

#     def separate_emitter(row):
#         emitter_pattern = r'([A-Za-z]+[.][A-Za-z]*.*)'
#         row['Emitters'] = re.search(emitter_pattern, row['yaw:'])
#         row['yaw:'] = re.sub(emitter_pattern,'',row['yaw:'])
#         return row


#     sam_df_list = []
#     def pop_row(row) -> pd.DataFrame: # this is in here because it inherits mutable flight_df and pops from inside the function
#         if row['Player:'].startswith('Sam'):
#             flight_df.drop(index=row.name,inplace=True)
#             sam_row = row[0]
#             sam_df_list.append([sam_row])
#             row = separate_emitter(row)
#         else:
#             pass
#         return flight_df


#     flight_df.apply(pop_row, axis=1)
#     sam_df = pd.DataFrame(sam_df_list)

    
#     flight_df = flight_df[flight_df['x:'].notnull()]
#     sub_pattern = r'["[\' \sA-Za-z0-9(/)]*:'
#     flight_df = flight_df.applymap(lambda x: re.sub(sub_pattern, '', x))
#     return (flight_df, sam_df)
