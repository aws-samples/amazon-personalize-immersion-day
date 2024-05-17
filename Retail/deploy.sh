#!/bin/bash

bucket=$1
echo "Bucket is $bucket"

pwd

mkdir poc_data
mkdir poc_data/data
mkdir poc_data/metadata

echo "Local copy sync Retail"

wget -P poc_data/data https://code.retaildemostore.retail.aws.dev/csvs/interactions.csv
wget -P poc_data/data https://code.retaildemostore.retail.aws.dev/csvs/items.csv
wget -P poc_data/data https://code.retaildemostore.retail.aws.dev/csvs/users.csv

sleep 60
echo "Starting the copy to S3 data"

aws s3 cp ./poc_data/data/users.csv s3://$bucket/train/retail/users.csv
aws s3 cp ./poc_data/data/interactions.csv s3://$bucket/train/retail/interactions.csv
aws s3 cp ./poc_data/data/items.csv s3://$bucket/train/retail/items.csv

sleep 60

aws s3 cp ./params.json s3://$bucket/train/retail/params.json