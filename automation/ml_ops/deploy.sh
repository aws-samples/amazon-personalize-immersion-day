#!/bin/bash

bucket=$1
echo "Bucket is $bucket"
echo "Domain is $2"
echo "Local copy sync Retail"
aws s3 cp s3://retail-demo-store-us-east-1/csvs/interactions.csv ./domain/Retail/data/Interactions/interactions.csv
aws s3 cp s3://retail-demo-store-us-east-1/csvs/users.csv ./domain/Retail/data/Users/users.csv
aws s3 cp s3://retail-demo-store-us-east-1/csvs/items.csv ./domain/Retail/data/Items/items.csv
aws s3 cp s3://retail-demo-store-us-east-1/data/products.yaml ./domain/Retail/metadata/Items/products.yaml
aws s3 cp s3://retail-demo-store-us-east-1/data/categories.yaml ./domain/Retail/metadata/Items/categories.yaml
aws s3 cp s3://retail-demo-store-us-east-1/data/users.json.gz ./domain/Retail/metadata/Users/users.json.gz

echo "Local copy sync CPG"
aws s3 cp s3://personalization-at-amazon/personalize-immersion-day/CPG/Interactions/interactions.csv ./domain/CPG/data/Interactions/interactions.csv
aws s3 cp s3://personalization-at-amazon/personalize-immersion-day/CPG/Items/items.csv ./domain/CPG/data/Items/items.csv
aws s3 cp s3://personalization-at-amazon/personalize-immersion-day/CPG/Users/users.csv ./domain/CPG/data/Users/users.csv
aws s3 cp s3://personalization-at-amazon/personalize-immersion-day/CPG/Metadata/users-origin.csv ./domain/CPG/data/metadata/users-origin.csv
aws s3 cp s3://personalization-at-amazon/personalize-immersion-day/CPG/Metadata/items-origin.csv ./domain/CPG/data/metadata/items-origin.csv

echo "Local copy sync Media"

mkdir poc_data
mkdir domain/Media/data/
mkdir domain/Media/data/Interactions/
mkdir domain/Media/data/Items/
cd poc_data 
wget http://files.grouplens.org/datasets/movielens/ml-latest-small.zip
unzip ml-latest-small.zip

echo "Local copy sync Media-Pretrained"
mkdir imdb

echo "IMDB data setup"
cd ..
aws s3 cp s3://elementalrodeo99-us-west-1/aim312/items.csv poc_data/imdb/items.csv
mkdir domain/Media-Pretrained/data/
mkdir domain/Media-Pretrained/data/Interactions/
mkdir domain/Media-Pretrained/data/Items/
mkdir domain/Media-Pretrained/data/Users/
aws s3 cp s3://elementalrodeo99-us-west-1/aim312/items.csv domain/Media-Pretrained/data/Items/
aws s3 cp s3://elementalrodeo99-us-west-1/aim312/users.csv domain/Media-Pretrained/data/Users/

# Movie Lens data is imported into poc_data for the Media above

pwd
if [ "$2" == "Media-Pretrained" ]
then
    echo "Preprocess the IMDB and Movielens data"

    ipython script-Pretrained.py >script-Pretrained.out 2>&1
    
else
    echo "Preprocess the Movielens data"
    python script.py
fi

sleep 60

if [ "$2" == "Retail-Pretrained" ]
then 
    echo "Starting the copy to S3 Retail data"
    aws s3 cp s3://retail-demo-store-us-east-1/csvs/users.csv s3://$bucket/train/users.csv
    aws s3 cp s3://retail-demo-store-us-east-1/csvs/items.csv s3://$bucket/train/items.csv
    aws s3 cp s3://retail-demo-store-us-east-1/csvs/interactions.csv s3://$bucket/train/interactions.csv
    aws s3 cp ./domain/$2/params.json s3://$bucket/train/params.json
elif [ "$2" = "Media" ]
then
    echo "Starting the copy to S3 Media data"
    aws s3 cp ./domain/$2/data/Items/item-meta.csv s3://$bucket/Items/items.csv
    aws s3 cp ./domain/$2/data/Interactions/interactions.csv s3://$bucket/Interactions/interactions.csv
    aws s3 cp ./domain/$2/params.json s3://$bucket 
elif [ "$2" = "CPG" ]
then
    echo "Starting the copy to S3 CPG data"
    aws s3 cp s3://personalization-at-amazon/personalize-immersion-day/CPG/Items/items.csv s3://$bucket/Items/items.csv
    aws s3 cp s3://personalization-at-amazon/personalize-immersion-day/CPG/Interactions/interactions.csv s3://$bucket/Interactions/interactions.csv
    aws s3 cp s3://personalization-at-amazon/personalize-immersion-day/CPG/Users/users.csv s3://$bucket/Users/users.csv
    aws s3 cp ./domain/$2/params.json s3://$bucket 
elif [ "$2" = "Media-Pretrained" ]
then
    echo "Starting the copy to S3 Media data"
    aws s3 cp ./poc_data/users.csv s3://$bucket/train/users.csv
    aws s3 cp ./poc_data/interactions.csv s3://$bucket/train/interactions.csv
    aws s3 cp ./poc_data/item-meta.csv s3://$bucket/train/items.csv
    aws s3 cp ./domain/$2/params.json s3://$bucket/train/params.json
fi
