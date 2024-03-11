#!/bin/bash

bucket=$1
echo "Bucket is $bucket"

pwd

echo "Preprocess the IMDB and Movielens data"
# this copies and prepares the media data 

# THIS SCRIPT IS GENREATED BY EXPORTING /Media/01_Data_Layer.ipynb
jupyter nbconvert --to python ./01_Data_Preparation.ipynb 
ipython ./01_Data_Preparation.py >./01_Data_Preparation.out 2>&1
# rm ./Media/01_Data_Preparation.py

sleep 120

echo "Starting the copy to S3 data"
aws s3 cp ./poc_data/users.csv s3://$bucket/train/media/users.csv
aws s3 cp ./poc_data/interactions.csv s3://$bucket/train/media/interactions.csv
aws s3 cp ./poc_data/items.csv s3://$bucket/train/media/items.csv

sleep 60

aws s3 cp ./params.json s3://$bucket/train/media/params.json