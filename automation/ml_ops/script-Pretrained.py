import numpy as np
import pandas as pd
import boto3
from datetime import datetime
import json
from time import sleep
import time
USE_FULL_MOVIELENS = False

# First, you will download the dataset from the Movielens website and unzip it in a new folder using the code below.

data_dir = "poc_data"
dataset_dir = data_dir + "/ml-latest-small/"

original_data = pd.read_csv(dataset_dir + '/ratings.csv',
                            sep=',', dtype={'userId': "int64", 'movieId': "str"})


links = pd.read_csv(dataset_dir + '/links.csv', sep=',', usecols=[
                    0, 1], encoding='latin-1', dtype={'movieId': "str", 'imdbId': "str", 'tmdbId': "str"})
pd.set_option('display.max_rows', 25)
links['imdbId'] = 'tt' + links['imdbId'].astype(object)

imdb_data = original_data.merge(links, on='movieId')
imdb_data.drop(columns='movieId')

watched_df = imdb_data.copy()
watched_df = watched_df[watched_df['rating'] > 3]
watched_df = watched_df[['userId', 'imdbId', 'timestamp']]
watched_df['EVENT_TYPE'] = 'Watch'

clicked_df = imdb_data.copy()
clicked_df = clicked_df[clicked_df['rating'] > 1]
clicked_df = clicked_df[['userId', 'imdbId', 'timestamp']]
clicked_df['EVENT_TYPE'] = 'Click'

interactions_df = clicked_df.copy()
interactions_df = interactions_df.append(watched_df)
interactions_df.sort_values("timestamp", axis=0, ascending=True,
                            inplace=True, na_position='last')
interactions_df.rename(columns={'userId': 'USER_ID', 'imdbId': 'ITEM_ID',
                                'timestamp': 'TIMESTAMP'}, inplace=True)

# We'll be using a subset of the IMDB dataset for this workshop that has been cleaned to remove movies that don't have valid values for the metadata we are using in out ITEMs dataset (we'll work with this more in the net section), so we'll need to make sure we don't have any interactions that have IMDB movie ids that are not in our subset of the IMDB data set.

imdb_dataset_dir = data_dir + "/imdb/"
movies = pd.read_csv(imdb_dataset_dir + '/items.csv', sep=',', usecols=[
                     0, 1], encoding='latin-1', dtype={'movieId': "str", 'imdbId': "str", 'tmdbId': "str"})
pd.set_option('display.max_rows', 25)

# Next, let's compare the number of ITEM_ID unique keys in the IMDB data to the ITEM_ID unique keys in the interactions.  They should be the same.

movies.nunique(axis=0)

interactions_df.nunique(axis=0)

# The number of unique ITEM_IDs are not the same in the IMDB data and the interactions data, so we'll clean out the data points with ITEM_IDs that do not match from interactions dataset.

interactions_df = interactions_df.merge(movies, on='ITEM_ID')
interactions_df = interactions_df.drop(columns=['TITLE'])
interactions_df.info()

# That's it! At this point the data is ready to go, and we just need to save it as a CSV file.

interactions_filename = "interactions.csv"
interactions_df.to_csv((data_dir+"/"+interactions_filename),
                       index=False, float_format='%.0f')

original_data = pd.read_csv(
    imdb_dataset_dir + '/items.csv', sep=',', dtype={'PROMOTION': "string"})


items_filename = "items.csv"
original_data.to_csv((data_dir+"/"+items_filename),
                     index=False, float_format='%.0f')

user_ids = interactions_df['USER_ID'].unique()
user_data = pd.DataFrame()
user_data["USER_ID"] = user_ids

# Adding Metadata
# The current dataset does not contain additiona user information. For this example, we'll randomly assign a membership level. For Ad Supported models this could indicate premium vs ad supported.

possible_membership_levels = ['silver', 'gold']
random = np.random.choice(possible_membership_levels,
                          len(user_data.index), p=[0.5, 0.5])
user_data["MEMBERLEVEL"] = random

# Saving the data as a CSV file
users_filename = "users.csv"
user_data.to_csv((data_dir+"/"+users_filename),
                 index=False, float_format='%.0f')
