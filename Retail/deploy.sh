#!/bin/bash

bucket=$1
echo "Bucket is $bucket"

pwd


echo "Starting the copy to S3 data"
# aws s3 cp ./poc_data/users.csv s3://$bucket/train/users.csv
# aws s3 cp ./poc_data/interactions.csv s3://$bucket/train/interactions.csv
# aws s3 cp ./poc_data/items.csv s3://$bucket/train/items.csv


aws s3 cp s3://retail-demo-store-us-east-1/csvs/users.csv s3://$bucket/train/users.csv
aws s3 cp s3://retail-demo-store-us-east-1/csvs/interactions.csv s3://$bucket/train/interactions.csv
aws s3 cp s3://retail-demo-store-us-east-1/csvs/items.csv s3://$bucket/train/items.csv

sleep 60

aws s3 cp ./params.json s3://$bucket/train/params.json

