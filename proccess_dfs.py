import pandas as pd
import pickle
with open ('nairaland_dfs', 'rb') as fp:
    data_frame = pickle.load(fp)
df = pd.concat((dfs for dfs in data_frame),axis=0)
df.reset_index(inplace=True)
