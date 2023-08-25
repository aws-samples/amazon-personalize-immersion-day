import pandas as pd

data_dir = "poc_data"
dataset_dir = data_dir + "/ml-latest-small/"

print("constructing interactions ")
original_data = pd.read_csv(dataset_dir + '/ratings.csv')
clicked_df = original_data.copy()
clicked_df = clicked_df[clicked_df['rating'] > 1]
clicked_df = clicked_df[['userId', 'movieId', 'timestamp']]
clicked_df['EVENT_TYPE']='click'

interactions_df = clicked_df.copy()

watched_df = original_data.copy()
watched_df = watched_df[watched_df['rating'] > 3]
watched_df = watched_df[['userId', 'movieId', 'timestamp']]
watched_df['EVENT_TYPE']='watch'

interactions_df = pd.concat([interactions_df, watched_df])
interactions_df.sort_values("timestamp", axis = 0, ascending = True, inplace = True, na_position ='last')
interactions_df.rename(columns = {'userId':'USER_ID', 'movieId':'ITEM_ID', 'timestamp':'TIMESTAMP'}, inplace = True)
interactions_filename = "interactions.csv"
interactions_df.to_csv(("./domain/Media/data/Interactions/"+interactions_filename), index=False, float_format='%.0f')

print("constructing items")
original_data = pd.read_csv(dataset_dir + '/movies.csv')
original_data['year'] =original_data['title'].str.extract('.*\((.*)\).*',expand = False)
original_data = original_data.dropna(axis=0)

itemmetadata_df = original_data.copy()
itemmetadata_df = itemmetadata_df[['movieId', 'genres', 'year']]
itemmetadata_df['CREATION_TIMESTAMP'] = 0
itemmetadata_df.rename(columns = {'genres':'GENRE', 'movieId':'ITEM_ID', 'year':'YEAR'}, inplace = True)
itemmetadata_filename = "item-meta.csv"
itemmetadata_df.to_csv(("./domain/Media/data/Items/"+itemmetadata_filename), index=False, float_format='%.0f')