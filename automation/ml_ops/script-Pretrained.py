# THIS SCRIPT IS GENREATED BY EXPORTING Media-Pretrain/notebooks/01_Data_Layer.ipynb

# Get the latest version of botocore to ensure we have the latest features in the SDK
import numpy as np
import pandas as pd
import boto3
from datetime import datetime
import json
from time import sleep
import time
import sys
get_ipython().system('{sys.executable} -m pip install --upgrade pip')
get_ipython().system(
    '{sys.executable} -m pip install --upgrade --no-deps --force-reinstall botocore')
data_dir = "poc_data"
get_ipython().system('mkdir $data_dir')


# In[2]:


# Configure the SDK to Personalize:
personalize = boto3.client('personalize')
personalize_runtime = boto3.client('personalize-runtime')


# If this is a workshop and the resources were created for you, we will retrieve the variables of the resources created.

# In[3]:


# Opening JSON file
f = open('../../automation/ml_ops/domain/Media-Pretrained/params.json')
parameters = json.load(f)


# In[4]:


workshop_dataset_group_name = parameters['datasetGroup']['serviceConfig']['name']

interactions_schema_name = parameters['datasets']['interactions']['schema']['serviceConfig']['name']
interactions_dataset_name = parameters['datasets']['interactions']['dataset']['serviceConfig']['name']

items_schema_name = parameters['datasets']['items']['schema']['serviceConfig']['name']
items_dataset_name = parameters['datasets']['items']['dataset']['serviceConfig']['name']

users_schema_name = parameters['datasets']['users']['schema']['serviceConfig']['name']
users_dataset_name = parameters['datasets']['users']['dataset']['serviceConfig']['name']

# The following job names are the starting Strings of the job names that can be created
interactions_import_job_name = 'dataset_import_interaction'
items_import_job_name = 'dataset_import_item'
users_import_job_name = 'dataset_import_user'

for recommender in parameters['recommenders']:
    # This is currently configured assuming only one recommender of each type, if there are multiple
    # recommenders of the same type further configuration is needed.
    if (recommender['serviceConfig']['recipeArn'] == 'arn:aws:personalize:::recipe/aws-vod-more-like-x'):
        recommender_more_like_x_name = recommender['serviceConfig']['name']
    if (recommender['serviceConfig']['recipeArn'] == 'arn:aws:personalize:::recipe/aws-vod-top-picks'):
        recommender_top_picks_for_you_name = recommender['serviceConfig']['name']

for solution in parameters['solutions']:
    # This is currently configured assuming only one solution of this type, if there are multiple
    # solutions of the same type further configuration is needed.
    if (solution['serviceConfig']['recipeArn'] == 'arn:aws:personalize:::recipe/aws-personalized-ranking'):
        workshop_rerank_solution_name = solution['serviceConfig']['name']
        # This is currently configured assuming only one campaign, if there are multiple campaigns
        # further configuration is needed.
        workshop_rerank_campaign_name = solution['campaigns'][0]['serviceConfig']['name']


# ## Introduction to Amazon Personalize Datasets <a class="anchor" id="datasets"></a>
# [Back to top](#top)

# Regardless of the use case, the algorithms all share a base of learning on user-item-interaction data which is defined by 3 core attributes:
#
# 1. **UserID** - The user who interacted
# 1. **ItemID** - The item the user interacted with
# 1. **Timestamp** - The time at which the interaction occurred
#
# Generally speaking your data will not arrive in a perfect form for Personalize, and will take some modification to be structured correctly. This notebook guides you through that process.
#
# ### Items data
#
# The item data consists of information about the content that is being interacted with, this generally comes from Content Management Systems (CMS). For the purpose of this workshop we will use the IMDb TT ID to provide a common identifier between the interactions data and the content metadata. Movielens provides its own identifier as well as a the IMDb TT ID (without the leading 'tt') in the 'links.csv' file. This dataset is not manatory, but provided good item metadata will ensure the best results in your trained models.
#
# ### Interactions data
#
# The interaction data concists of information about the interactions the users of the fictional app will have with the content. This usually comes from analytics tools or Customer Data Platform's (CDP). The best interaction data for use for Amazon Personalize would include the sequential order of user beavior, what content was watched/clicked on and the order it was interacted with. To simulate our interaction data, we will be using data from the [MovieLens project](https://grouplens.org/datasets/movielens/). Movielens offers multiple versions of their dataset, for the purposes of this workshop we will be using the reduced version of this dataset (approx 100,000 ratings and 3,600 tag applications applied to 9,000 movies by 600 users).
#
# ### User data
#
# The user data is what information you have about you users, it usually comes from Customer relationship management (CRM) or Subscriber management systems. Since there is no user data included in the MovieLens data, we will be generating a small synthetic dataset to simulate this component of the workshop. This dataset is not manatory, but provided good item metadata will ensure the best results in your trained models
#
# In this notebook we will be importing interactions, user and item data into your environment, inspecting it and converting it to a format that will allow you use it in Amazon Personalize to train models to get personalized recommendations.
#
# The following diagram shows the resources that we will create in this section. with the section we are building  in this notebook highlighted in blue with a dashed outline.
#
# ![Workflow](images/01_Data_Layer_Resources.jpg)

# ## Prepare the Item Metadata <a class="anchor" id="prepare_items"></a>
# [Back to top](#top)

# Our fictional streaming service UnicornFlix has a massive catalog of over 9000 titles, which were acquired from many different sources, one challenge we have is that the catalog metadata is not standardized across all of these titles, and it is not very detailed. In order provide additional metadata for Amazon Personalize to use, and also to provide a consistent experience for our users we will leverage the IMDb Essential Metadata for Movies/TV/OTT dataset, which contains
#
# - 9+ million titles
# - 12+ million names
# - Film, TV, music and celebrities
# - 1 billion ratings from the world’s largest entertainment fan community
#
# IMDb has multiple datasets available in the Amazon Data Exchange
# https://aws.amazon.com/marketplace/seller-profile?id=0af153a3-339f-48c2-8b42-3b9fa26d3367
#
# For this workshop we have already extracted the data we needed and prepared it for use with the following information from the IMDb Essential Metadata for Movies/TV/OTT (Bulk data) dataset.
#
# TITLE
# YEAR
# IMDB_RATING
# IMDB_NUMBEROFVOTES
# PLOT
# US_MATURITY_RATING_STRING
# US_MATURITY_RATING
# GENRES
#
# In addition we added two fields that will help us with our fictional use case. Note: these are not derived from the  IMDb dataset
#
# CREATION_TIMESTAMP
# PROMOTION
#
#
# NOTE:
# Your use of IMDb data is for the sole purpose of completing the AWS workshop and/or tutorial. Any use of IMDb data outside of the AWS workshop and/or tutorial requires a data license from IMDb. To obtain a data license, please contact: imdb-licensing-support@imdb.com. You will not (and will not allow a third party to) (i) use IMDb data, or any derivative works thereof, for any purpose; (ii) copy, sublicense, rent, sell, lease or otherwise transfer or distribute IMDb data or any portion thereof to any person or entity for any purpose not permitted within the workshop and/or tutorial; (iii) decompile, disassemble, or otherwise reverse engineer or attempt to reconstruct or discover any source code or underlying ideas or algorithms of IMDb data by any means whatsoever; or (iv) knowingly remove any product identification, copyright or other notices from IMDb data.

# Copy the IMDB item metadata that was added to this notebook instance during automated deployment of the workshop.

# In[5]:


get_ipython().system('mkdir poc_data/imdb')
get_ipython().system('cp ../../automation/ml_ops/poc_data/imdb/items.csv poc_data/imdb')


# Next, load the IMDB `items.csv` file and take a look at the first rows. This file has information about the movie.

# In[6]:


item_data = pd.read_csv(data_dir + '/imdb/items.csv',
                        sep=',', dtype={'PROMOTION': "string"}, index_col=0)
item_data.head(5)


# In[7]:


item_data.describe()


# This does not really tell us much about the dataset, so we will explore a bit more and look at the raw information. We can see that genres often appear in groups. That is fine for us as Personalize supports this structure.

# In[8]:


item_data.info()


# Now we have our Catalog of titles that our service offers. We also have some movies that the UnicornFlix marketing department would like to ensure are promoted in our recommendations. Amazon Personalize has a feature that allows you to promote items into recommendations, and set the balance of promoted items vs recommendations (we will cover this in detail in `03_Inference_Layer.ipynb`. Since we are in Las Vegas, lets create a promotion for movies about or set in Las Vegas. First we will find the movies in our catalog that feature or are set in/about Las Vegas and set the metadata field to true.

# In[9]:


mask = item_data['PLOT'].str.contains('las vegas', case=False, na=False)
item_data.loc[mask, 'PROMOTION'] = 'true'
item_metadata = item_data
item_data[mask]


# lets confirm that the changes we have made, have not introduced any null values

# In[10]:


item_data.isnull().sum()


# Looks good, we currently have no null values.

# That's it! At this point the item data is ready to go, and we just need to save it as a CSV file.

# In[11]:


items_filename = "item-meta.csv"
item_data.to_csv((data_dir+"/"+items_filename),
                 index=True, float_format='%.0f')


# ## Prepare the Interactions data
#
# First, you will download the dataset from the [MovieLens project](https://grouplens.org/datasets/movielens/) website and unzip it in a new folder using the code below.

# In[12]:


get_ipython().system(
    'cd $data_dir && wget http://files.grouplens.org/datasets/movielens/ml-latest-small.zip')
get_ipython().system('cd $data_dir && unzip -o ml-latest-small.zip')
dataset_dir = data_dir + "/ml-latest-small/"


# Take a look at the data files you have downloaded.

# In[13]:


get_ipython().system('ls $dataset_dir')


# We can look at the README.txt file and licensing, do not skip over usage license!

# In[14]:


get_ipython().system('pygmentize $data_dir/ml-latest-small/README.txt')


# The primary data we are interested in for a recommendation use case is the actual interactions that the users had with the titles(items).
#
# Open the `ratings.csv` file and take a look at the some rows from throughout the dataset.

# In[15]:


interaction_data = pd.read_csv(
    dataset_dir + '/ratings.csv', sep=',', dtype={'userId': "int64", 'movieId': "str"})
interaction_data.sample(10)


# To use Amazon Personalize, you need to save timestamps in Unix Epoch format.
#
# Lets validate that the timestamp is actually in a Unix Epoch format by converting it into a more easily understood time/date format

# In[16]:


arb_time_stamp = interaction_data.iloc[50]['timestamp']
print('timestamp')
print(arb_time_stamp)
print()
print('Date & Time')
print(datetime.utcfromtimestamp(arb_time_stamp).strftime('%Y-%m-%d %H:%M:%S'))


# We will do some general summarization and inspection of the data to ensure that it will be helpful for Amazon Personalize

# In[17]:


interaction_data.isnull().any()


# In[18]:


interaction_data.info()


# What you can see is that the Movielens dataset is that this dataset contains a userid, a movie id, the rating that the user gave the movie and the time the made this interaction. For the purposes of our fictional setvice UnicornFlix will stand in for our applications interaction data, which would actually be the click stream data of the titles that were watched, in the order they watched them.

# ### Convert the Interactions Data
#
# The interaction data generally is acquired from anaytics or CDP platforms that can identify individual interactions with content/items within a platform.
#
# We need to do a few things to get this dataset ready to subsitute for our services interaction data.
#
# First off, the movieId is a unique identifier provided by Movielens for each tite. However as we saw above IMDb has a much richer set of metadata about the content catalog. In order to use the IMDb data we will need to use a common  identifier between our items and our interactions dataset, which is the IMDb imdbId. To do this Movielens provides the 'links.csv' file which helps convert between the two identifiers.

# In[19]:


links = pd.read_csv(dataset_dir + '/links.csv', sep=',', usecols=[
                    0, 1], encoding='latin-1', dtype={'movieId': "str", 'imdbId': "str", 'tmdbId': "str"})
pd.set_option('display.max_rows', 25)
links['imdbId'] = 'tt' + links['imdbId'].astype(object)
links


# As you can see this provides a method to identify what the IMDb id is for every title in our interactions dataset, now we will convert the ratings.csv data to utilize the IMDb ID.

# In[20]:


imdb_data = interaction_data.merge(links, on='movieId')
imdb_data.drop(columns='movieId')


# Now we have a interactions dataset that matches our item catalog dataset.
#
# ### Simulating a interaction dataset
#
# We are going to make one more modification to make the MoviesLens dataset more like the analytics data that a video streaming service would see in their interactions. MoviesLens is an explicit movie rating dataset, which means users are presented a movie and asked to give it a rating. For recommendation systems/personalization, the industry has moved on to using more implicit data. This is due to many reasons including low numbers of customers rating titles and customers tastes changing over time. Some of the benefits of implicit interaction data is that it is the actual behavior of all users and changes over time as their viewing behavior changes.
#
# To convert the explicit interaction MovieLens ratings dataset into our fictional streaming service UnicornFlix's implicit dataset we are going to create a synthetic dataset using the ratings in MovieLens.
#
# - Implicit interactions are inherently positive interactions so we will be dropping any rating that is below 2 stars
# - Ratings of 2 and 3 stars are neutral to slightly positive, we are going to create synthetic "Click" events to simulate a viewer clicking on a title in the UnicornFlix app
# - Ratings of 4 and 5 are overwhelmingly positive, we will use these to create synthetic "Watch" and "Click" events to simulate a viewer both clicking on a title and watching at least 80% of a title in the UnicornFlix app
#
# NOTE: This will be directionaly accurate, but is not a good substite for actual temporal based interaction data, the order that viewers rated movies on the MovieLens website is not as good as the order of interactions on an actual Video On Demand Streaming app. For more information about the importance of the temporal interaction data see
# https://www.amazon.science/publications/temporal-contextual-recommendation-in-real-time

# In[21]:


watched_df = imdb_data.copy()
watched_df = watched_df[watched_df['rating'] > 3]
watched_df = watched_df[['userId', 'imdbId', 'timestamp']]
watched_df['EVENT_TYPE'] = 'Watch'
watched_df.head()


# In[22]:


clicked_df = imdb_data.copy()
clicked_df = clicked_df[clicked_df['rating'] > 1]
clicked_df = clicked_df[['userId', 'imdbId', 'timestamp']]
clicked_df['EVENT_TYPE'] = 'Click'
clicked_df.head()


# In[23]:


interactions_df = clicked_df.copy()
interactions_df = pd.concat([interactions_df, watched_df])
interactions_df.sort_values("timestamp", axis=0, ascending=True,
                            inplace=True, na_position='last')

# Lets look at what the new dataset looks like and ensure that the data reflects our fictional streaming services streaming analytics data

# In[24]:


interactions_df


#  Amazon Personalize has default column names for users, items, and timestamp. These default column names are `USER_ID`, `ITEM_ID`, `TIMESTAMP` and `EVENT_VALUE` for the [VIDEO_ON_DEMAND domain dataset](https://docs.aws.amazon.com/personalize/latest/dg/VIDEO-ON-DEMAND-datasets-and-schemas.html). The final modification to the dataset is to replace the existing column headers with the default headers.

# In[25]:


interactions_df.rename(columns={'userId': 'USER_ID', 'imdbId': 'ITEM_ID',
                                'timestamp': 'TIMESTAMP'}, inplace=True)


# We'll be using a subset of the IMDB dataset for this workshop that has been cleaned to remove movies that don't have valid values for the metadata we are using in out ITEMs dataset (we'll work with this more in the net section), so we'll need to make sure we don't have any interactions that have IMDB movie ids that are not in our subset of the IMDB data set.

# In[26]:


movies = pd.read_csv(data_dir + '/imdb' + '/items.csv', sep=',', usecols=[
                     0, 1], encoding='latin-1', dtype={'movieId': "str", 'imdbId': "str", 'tmdbId': "str"})
pd.set_option('display.max_rows', 25)


# Next, let's compare the number of ITEM_ID unique keys in the IMDB data to the ITEM_ID unique keys in the interactions.  They should be the same.

# In[27]:


movies.nunique(axis=0)


# The number of unique ITEM_IDs are not the same in the IMDB data and the interactions data, so we'll clean out the data points with ITEM_IDs that do not have item metadata from the interactions dataset.

# In[28]:


interactions_df = interactions_df.merge(movies, on='ITEM_ID')
interactions_df.info()


# We will also drop the `TITLE` column as it is not required in the interactions dataset.

# In[29]:


interactions_df = interactions_df.drop(columns=['TITLE'])
interactions_df.info()


# That's it! At this point the data is ready to go, and we just need to save it as a CSV file.

# In[30]:


interactions_filename = "interactions.csv"
interactions_df.to_csv((data_dir+"/"+interactions_filename),
                       index=False, float_format='%.0f')


# ## Prepare the User Metadata <a class="anchor" id="prepare_users"></a>
# [Back to top](#top)
#
# The dataset does not have any user metadata so we will create a synthetic metadata field that would be an example of the type of user metadata UnicornFlix may have in their CRM/Subcriber management system. This data will be used both for training of the models, but also can be used for inference filters, which will be covered in a later notebook.

# In[31]:


# get all unique user ids from the interaction dataset

user_ids = interactions_df['USER_ID'].unique()
user_data = pd.DataFrame()
user_data["USER_ID"] = user_ids
user_data


# ### Adding User Metadata
#
# The current dataset does not contain additiona user information. For this example, we'll randomly assign a membership level. For Ad Supported models this could indicate premium vs ad supported.
#
# NOTE: This is a synthetic dataset and since it is randomly assigned, will be of little value to our mode, in a real world scenario this data would be accurate to the user data.

# In[32]:


possible_membership_levels = ['silver', 'gold']
random = np.random.choice(possible_membership_levels,
                          len(user_data.index), p=[0.5, 0.5])
user_data["MEMBERLEVEL"] = random
user_data


# That's it! At this point the data is ready to go, and we just need to save it as a CSV file.

# In[33]:


# Saving the data as a CSV file
users_filename = "users.csv"
user_data.to_csv((data_dir+"/"+users_filename),
                 index=False, float_format='%.0f')