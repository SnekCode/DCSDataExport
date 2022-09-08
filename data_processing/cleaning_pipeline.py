from clean_utils import read_logs, read_log_file_contents, drop_clean_runs, t_until_impact, find_first_RWR_lock, time_since_lock_on, drop_early_and_late_runs
from tqdm import tqdm
import pandas as pd


data_path = r'./data'
dataset_labels, dataset_log_titles = read_logs(data_path=data_path) # data is tuple(maneuver, tuple(log_filename, log_contents))

dataset_dfs = []
dataset_event_dfs = []
for i, l in enumerate(dataset_labels): 
    dfs = []
    event_dfs = []
    print(f'Importing "{l}" dataset...')
    for t in tqdm(dataset_log_titles[i]):
        df, event_df = read_log_file_contents(l,t,data_path+ '/' + l + '/' + t)
        dfs.append(df)
        event_dfs.append(event_df)

    dataset_dfs.append(dfs)
    dataset_event_dfs.append(event_dfs)


for i, dataset in tqdm(enumerate(dataset_dfs)):
    dataset_dfs[i], dataset_event_dfs[i] = drop_clean_runs(dataset_dfs[i], dataset_event_dfs[i]) 

master_dataset = pd.DataFrame(columns=['CATEGORY', 'RUN_ID', 'TIME', 'ALT', 'SPEED', 'PITCH', 'BANK', 'RWR', 'GT_MISSILE_DIST', 'T_UNTIL_IMPACT','TIME_SINCE_LOCK'])
for i, dataset in tqdm(enumerate(dataset_dfs)):
    print(f'Cleaning "{dataset_labels[i]}" dataset...')
    for j, df in enumerate(dataset):
        impact = dataset_event_dfs[i][j].iloc[0,2] # dont with dataset_event_dfs now
        dataset_dfs[i][j] = dataset_dfs[i][j].apply(t_until_impact, axis=1, impact=impact)
        first_lock_index = find_first_RWR_lock(dataset_dfs[i][j]['RWR'])
        first_lock_t = dataset_dfs[i][j].iloc[first_lock_index, 2]
        dataset_dfs[i][j] = dataset_dfs[i][j].apply(time_since_lock_on, axis=1, first_lock_t=first_lock_t)
        dataset_dfs[i][j] = drop_early_and_late_runs(dataset_dfs[i][j])
        master_dataset = master_dataset.append(dataset_dfs[i][j],ignore_index=True)

# merge dfs here
master_dataset.to_csv(data_path + '/' + 'master_df.csv')
# save dfs here


#cleaned_dfs = 