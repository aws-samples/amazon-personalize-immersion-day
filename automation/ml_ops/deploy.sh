#!/bin/bash
sudo service docker start
sudo usermod -a -G docker ec2-user
docker ps
pip install aws-sam-cli
sam --version
sam deploy --template-file template.yaml --stack-name id-ml-ops --capabilities CAPABILITY_IAM --s3-bucket $1
bucket=$(aws cloudformation describe-stacks --stack-name id-ml-ops --query "Stacks[0].Outputs[?OutputKey=='InputBucketName'].OutputValue" --output text)

echo "Local copy sync Retail"
wget -P domain/Retail/data/Interactions https://code.retaildemostore.retail.aws.dev/csvs/interactions.csv
wget -P domain/Retail/data/Items https://code.retaildemostore.retail.aws.dev/csvs/items.csv
wget -P domain/Retail/data/Users https://code.retaildemostore.retail.aws.dev/csvs/users.csv
wget -P domain/Retail/metadata/Items https://code.retaildemostore.retail.aws.dev/data/products.yaml
wget -P domain/Retail/metadata/Items https://code.retaildemostore.retail.aws.dev/data/categories.yaml
wget -P domain/Retail/metadata/Users https://code.retaildemostore.retail.aws.dev/data/users.json.gz

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
cd ..
python script.py

sleep 60

if [ "$2" == "Retail" ]
then
    echo "Starting the copy to S3 Retail data"
    aws s3 cp ./domain/Retail/data/Interactions/interactions.csv s3://$bucket/Interactions/interactions.csv
    aws s3 cp ./domain/Retail/data/Items/items.csv s3://$bucket/Items/items.csv
    aws s3 cp ./domain/Retail/data/Users/users.csv s3://$bucket/Users/users.csv
    aws s3 cp ./domain/Retail/params.json s3://$bucket
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
fi

