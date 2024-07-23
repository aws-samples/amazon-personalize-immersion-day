#!/bin/bash

bucket=$1
echo "Bucket is $bucket"

echo "Local copy sync Travel data"
#copy stuff here

mkdir poc_data
sleep 30

# need to fix this to point to cloudfront
aws s3 cp s3://personalize-solution-staging-us-east-1/personalize-immersionday-travel/travel_interactions.csv ./poc_data/travel_interactions.csv
aws s3 cp s3://personalize-solution-staging-us-east-1/personalize-immersionday-travel/travel_items.csv ./poc_data/travel_items.csv
aws s3 cp s3://personalize-solution-staging-us-east-1/personalize-immersionday-travel/travel_users.csv ./poc_data/travel_users.csv

sleep 30

echo "Starting the copy to S3 News Data"
aws s3 cp ./poc_data/travel_interactions.csv s3://$bucket/train/travel/interactions.csv
aws s3 cp ./poc_data/travel_items.csv s3://$bucket/train/travel/items.csv
aws s3 cp ./poc_data/travel_users.csv s3://$bucket/train/travel/params.json