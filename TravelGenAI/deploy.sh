#!/bin/bash

bucket=$1
echo "Bucket is $bucket"

echo "Local copy sync Travel data"
#copy stuff here

mkdir poc_data
sleep 30

wget -P poc_data https://d2peeor3oplhc6.cloudfront.net/personalize-immersionday-travel/travel_users.csv  
wget -P poc_data https://d2peeor3oplhc6.cloudfront.net/personalize-immersionday-travel/travel_items.csv  
wget -P poc_data https://d2peeor3oplhc6.cloudfront.net/personalize-immersionday-travel/travel_interactions.csv  

sleep 30

echo "Starting the copy to S3 to trigger automation process"
aws s3 cp ./poc_data/travel_interactions.csv s3://$bucket/train/travel/interactions.csv
aws s3 cp ./poc_data/travel_items.csv s3://$bucket/train/travel/items.csv
aws s3 cp ./poc_data/travel_users.csv s3://$bucket/train/travel/params.json