#!/bin/bash

bucket=$1
echo "Bucket is $bucket"
echo "Domain is $2"

if [ "$2" == "Retail-Pretrained" ]
then
    echo "Local copy sync Retail"
    wget -P domain/Retail-Pretrained/data/Interactions https://code.retaildemostore.retail.aws.dev/csvs/interactions.csv
    wget -P domain/Retail-Pretrained/data/Items https://code.retaildemostore.retail.aws.dev/csvs/items.csv
    wget -P domain/Retail-Pretrained/data/Users https://code.retaildemostore.retail.aws.dev/csvs/users.csv
    wget -P domain/Retail-Pretrained/metadata/Items https://code.retaildemostore.retail.aws.dev/data/products.yaml
    #wget -P domain/Retail-Pretrained/metadata/Items https://code.retaildemostore.retail.aws.dev/data/categories.yaml
    wget -P domain/Retail-Pretrained/metadata/Users https://code.retaildemostore.retail.aws.dev/data/users.json.gz

elif [ "$2" = "Media-Pretrained" ] || [ "$2" = "Media" ]
then
    echo "Local copy sync Movielens Data"

    mkdir poc_data
    mkdir domain/Media/data/
    mkdir domain/Media/data/Interactions/
    mkdir domain/Media/data/Items/
    cd poc_data
    wget http://files.grouplens.org/datasets/movielens/ml-latest-small.zip
    unzip ml-latest-small.zip
fi
if [ "$2" = "Media-Pretrained" ]
then
    echo "Local copy sync IMDB Data"
    mkdir imdb

    echo "IMDB data setup"
    cd ..
    wget -P poc_data/imdb https://d2peeor3oplhc6.cloudfront.net/personalize-immersionday-media/datasets/items.csv

    mkdir domain/Media-Pretrained/data/
    mkdir domain/Media-Pretrained/data/Interactions/
    mkdir domain/Media-Pretrained/data/Items/
    mkdir domain/Media-Pretrained/data/Users/
    wget -P domain/Media-Pretrained/data/Items https://d2peeor3oplhc6.cloudfront.net/personalize-immersionday-media/datasets/items.csv
    wget -P domain/Media-Pretrained/data/Users https://d2peeor3oplhc6.cloudfront.net/personalize-immersionday-media/datasets/users.csv
fi

# Movie Lens data is imported into poc_data for the Media above

pwd
if [ "$2" == "Media-Pretrained" ]
then
    echo "Preprocess the IMDB and Movielens data"

    ipython script-Pretrained.py >script-Pretrained.out 2>&1

elif [ "$2" = "Media" ]
then
    echo "Preprocess the Movielens data"
    python script.py

fi

sleep 60

if [ "$2" == "Retail-Pretrained" ]
then
    echo "Starting the copy to S3 Retail data"
    aws s3 cp ./domain/$2/data/Interactions/interactions.csv s3://$bucket/train/interactions.csv
    aws s3 cp ./domain/$2/data/Items/items.csv s3://$bucket/train/items.csv
    aws s3 cp ./domain/$2/data/Users/users.csv s3://$bucket/train/users.csv
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
