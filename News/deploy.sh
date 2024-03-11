#!/bin/bash

bucket=$1
echo "Bucket is $bucket"
echo "domain is $2"

echo "Local copy sync CI&T Deskdrop News Dataset"
#copy stuff here

mkdir poc_data

aws s3 cp s3://personalize-solution-staging-us-east-1/personalize-news-immersion-day/deskdrop_articles_automated.csv ./poc_data/deskdrop_articles_automated.csv 
aws s3 cp s3://personalize-solution-staging-us-east-1/personalize-news-immersion-day/deskdrop_interactions_automated.csv ./poc_data/deskdrop_interactions_automated.csv 

aws s3 cp s3://personalize-solution-staging-us-east-1/personalize-news-immersion-day/shared_articles.csv ./poc_data/shared_articles.csv
aws s3 cp s3://personalize-solution-staging-us-east-1/personalize-news-immersion-day/users_interactions.csv ./poc_data/user_interactions.csv

sleep 60
echo "Starting the copy to S3 News Data"
aws s3 cp ./poc_data/deskdrop_interactions_automated.csv s3://$bucket/train/news/interactions.csv
aws s3 cp ./poc_data/deskdrop_articles_automated.csv s3://$bucket/train/news/items.csv
aws s3 cp ./poc_data/params.json s3://$bucket/train/news/params.json