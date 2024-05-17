# Amazon Personalize Immersion Day

Amazon Personalize is a machine learning service that allows you to build and scale recommendation/personalization models in a quick and effective manner. The content below is designed to help you build out your first models for your given use cases.

## Introduction to Amazon Personalize

If you are not familiar with Amazon Personalize, you can learn more about the service on these pages:

* [Product Page](https://aws.amazon.com/personalize/)
* [GitHub Sample Notebooks](https://github.com/aws-samples/amazon-personalize-samples)
* [Product Documentation](https://docs.aws.amazon.com/personalize/latest/dg/what-is-personalize.html)

## Goals

By the end of this Immersion Day, you should have picked up the following skills:

1. How to map datasets to Amazon Personalize.
1. Which models or recipes are appropriate for which use cases.
1. How to build models in a programmatic fashion.
1. How to interpret model metrics.
1. How to deploy models in a programmatic fashion.
1. How to obtain recommendations from Amazon Personalize.
1. How to apply business rules to your recommendations.

## Process:

There are currenlty three versions of the Amazon Personalize Immersion Day

1. [Amazon Personalize for Media Immersion Day](./Media-Pretrained/README.md) 
1. [Amazon Personalize for Retail Immersion Day](./Retail-Pretrained/README.md)
1. [Amazon Personalize for News Immersion Day](./News-Pretrained/README.md) (Not Availible ATM)

All contain the respective notebooks for:  

1. Data -
`01_Data_Layer.ipynb`
1. Training -
`02_Training_Layer.ipynb`
1. Inference -
`03_Inference_Layer.ipynb`
1. Clean Up -
`04_Clean_Up.ipynb`

## Deploying Your Working Environment

1. Train as you go by executing each cell. Some cells may take a long time to finish executing as they wait for resources to be created. To do this simply run the notebooks all the way through - you will likely need to give the notebooks appropriate permissions to do this. To learn more about properly permissioning your SageMaker notebooks and account in general to use Amazon Personalize [see here](https://docs.aws.amazon.com/personalize/latest/dg/security-iam.html)

2. Go through notebook with previously created resources. All or the majority of the resources will already be created and cells will just retrieve the information of these existing resources to use them in following steps. 

To pre-provision resources and pre-train models, you can deploy the 'pretrained' Amazon CloudFormation template ([PersonalizeIDPretrained.yaml](../PersonalizeIDPretrained.yaml)) or click on the buttons below after logging into your AWS account.

> [!IMPORTANT]  
> Make sure to specify the right domain for your immersion day, either 'Media', 'Retail' or 'News' so the right resources are provisioned.

| Region | Region Code | Launch stack | 
|--------|--------|--------------|
| US East (N. Virginia) | us-east-1 | [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=PersonalizeExample&templateURL=https://personalize-solution-staging-us-east-1.s3.amazonaws.com/personalize-immersionday-template/PersonalizeIDPretrained.yaml) |
| Europe (Ireland) | eu-west-1 | [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/new?stackName=PersonalizeExample&templateURL=https://personalize-solution-staging-eu-west-1.s3.eu-west-1.amazonaws.com/personalize-immersionday-template/PersonalizeIDPretrained.yaml) |
| Asia Pacific (Sydney) | ap-southeast-2 |[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=ap-southeast-2#/stacks/new?stackName=PersonalizeExample&templateURL=https://personalize-solution-staging-ap-southeast-2.s3.ap-southeast-2.amazonaws.com/personalize-immersionday-template/PersonalizeIDPretrained.yaml) |

## Additional Instructions

For additional Instructions please visit our Amazon Personalize Immersion Day [Workshop Website](https://personalization-immersionday.workshop.aws/en/)

## Regions

This workshop has been tested in the Oregon (us-west-2), North Viginia (us-east-1) and Ireland (eu-west-1) regions.

## Costs

If you are running this workshop in your AWS account, you are going to create AWS resources that have a cost. Follow the steps in the 'Cleaning Up' section, even if you did not complete it, to avoid incurring unnecessary costs. 

## Cleaning Up

Finished with the Immersion Day? 

1. If you want to delete the resources created in your AWS account while following along with these notebooks, please see the `Clean_Up.ipynb` notebook. It will help you identify all of the Personalize resources deployed in your account and shows you how to delete them.

2. Delete the stack you created with CloudFormation. To do this, in the AWS Console again click the `Services` link at the top, and this time enter in `CloudFormation` and click the link for it. Then Click the `Delete` button on the stack you created.

Once you see `Delete Completed` you know that all resources created have been deleted.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.