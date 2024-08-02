#!/bin/bash

bucket=$1
echo "Bucket is $bucket"

echo "Local copy sync CI&T Deskdrop News Dataset"
#copy stuff here

mkdir poc_data
sleep 30

wget -P poc_data https://d2peeor3oplhc6.cloudfront.net/personalize-news-immersion-day/deskdrop_interactions_automated.csv
wget -P poc_data https://d2peeor3oplhc6.cloudfront.net/personalize-news-immersion-day/deskdrop_articles_automated.csv

sleep 30

echo "Starting the copy to S3 News Data"
aws s3 cp ./poc_data/deskdrop_interactions_automated.csv s3://$bucket/train/news/interactions.csv
aws s3 cp ./poc_data/deskdrop_articles_automated.csv s3://$bucket/train/news/items.csv
aws s3 cp ./params.json s3://$bucket/train/news/params.json