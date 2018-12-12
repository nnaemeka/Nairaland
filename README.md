# Nairaland
The code scraps Nairaland. www.nairaland.com, Nigeria's foremost social medium. It collects statistic such as users, 
gender, post title, classes of post, comments enterd by others etc and store it as pandas dataframe.
There are two dataframe. one contains a list of dataframe from each post. this dataframe is to save processed posts so 
that should there be connection timeout one can still have processed posts. the other dataframe contains all processd 
posts should the script run to end. One should concatenate the dataframes in the former, to get all the dataframes into single data frames.
the code to do this is included as process_dfs.py 
