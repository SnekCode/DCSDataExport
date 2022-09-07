from clean import read_logs

data_path = r'./data'
data = read_logs(data_path=data_path) # data is tuple(maneuver, tuple(log_filename, log_contents))
#print(data[1][0][1])