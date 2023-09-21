# Amazon Personalize Retail Immersion Day

Amazon Personalize is a machine learning service that allows you to build and scale recommendation/personalization models in a quick and effective manner. The content below is designed to help you build out your first models for your given use case and makes assumptions that your data may not yet be in an ideal format for Amazon Personalize to use.

This repository assumes a base familiarity with the service and if you have not already done so it is recommended that you use the getting-started material below.

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
1. How to obtain recommendations from Personalize.

## Process:

1. Deploying your working environment [see below]
1. Data Layer -
`01_Data_Layer.ipynb`
1. Training Layer -
`02_Training_Layer.ipynb`
1. Inference Layer -
`03_Inference_Layer.ipynb`
1. Operations Layer -
`04_Operations_Layer.ipynb`
1. Clean Up -
`05_Clean_Up.ipynb`

## Deploying Your Working Environment

As mentioned above, the first step is to deploy a CloudFormation template that will perform much of the initial setup work for you. In another browser window or tab, login to your AWS account. Once you have done that, open the link below in a new tab to start the process of deploying the items you need via CloudFormation.

| Region name | Region code | Launch      |
| ----------- | ----------- | ----------- |
| US East (N. Virginia)| us-east-1      |[![Launch Stack](./images/launch-cf-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=AmazonPersonalizeImmersionDay&templateURL=https://personalize-solution-staging-us-east-1.s3.amazonaws.com/personalize-immersionday-retail/personalizeimmersionday-retail.yaml) |
| US West (Oregon)   | us-west-2       |[![Launch Stack](./images/launch-cf-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=AmazonPersonalizeImmersionDay&templateURL=https://personalize-solution-staging-us-west-2.s3.us-west-2.amazonaws.com/personalize-immersionday-retail/personalizeimmersionday-retail.yaml) |
| Europe (Ireland)   | eu-west-1       |[![Launch Stack](./images/launch-cf-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/new?stackName=AmazonPersonalizeImmersionDay&templateURL=https://personalize-solution-staging-eu-west-1.s3.eu-west-1.amazonaws.com/personalize-immersionday-retail/personalizeimmersionday-retail.yaml) |

Follow along with the screenshots below if you have any questions about deploying the stack.

### CloudFormation Wizard

Start by clicking `Next` at the bottom like this:

![StackWizard](static/imgs/img1.png)

On this page you have a few options:

1. Enter a Stack name to something relevant like `AmazonPersonalizeImmersionDay`.
1. Change the SageMaker notebook instance name (optional).
1. Alter the SageMaker notebook EBS volume size, default is 64GB.
1. Select the industry domain you wish to use for the Immersion Day (Media, Retail, or CPG). Datasets and notebooks for the selected industry will be deployed in the SageMaker notebook instance.

When you are done click `Next` at the bottom.

![StackWizard2](static/imgs/img2.png)

This page is a bit longer, so scroll to the bottom to click `Next`. All of the defaults should be sufficient to complete the POC, if you have custom requirements, alter as necessary.

![StackWizard3](static/imgs/img3.png)


Again scroll to the bottom, check the box to enable the template to create new IAM resources and then click `Create Stack`.

![StackWizard4](static/imgs/img4.png)

For a few minutes CloudFormation will be creating the resources described above on your behalf it will look like this while it is provisioning:

![StackWizard5](static/imgs/img5.png)

Once it has completed you'll see green text like below indicating that the deployment has completed:

![StackWizard5](static/imgs/img6.png)

Now that your environment has been created go to the service page for SageMaker by clicking `Services` in the top of the console and then searching for `SageMaker` and clicking the service.


![StackWizard5](static/imgs/img7.png)

From the SageMaker console, scroll until you see the green box indicating now many notebooks you have in service and click that.

![StackWizard5](static/imgs/img8.png)

On this page you will see a list of any SageMaker notebooks you have running, click the `Open JupyterLab` link on the Amazon Personalize Immersion Day notebook you have created.

![StackWizard5](static/imgs/img9.png)

This will open the Jupyter environment for your Immersion Day; think of it as a web based data science IDE if you are not familiar with it.

### Additional Instructions

For additional Instructions please visit our Amazon Personalize Immersion Day [Workshop Website](https://personalization-immersionday.workshop.aws/en/)

### Cleaning Up

Finished with the Immersion Day? If you want to delete all the resources created in your AWS account while following along with these notebooks, please see the `05_Clean_Up.ipynb` notebook. It will help you identify all of the Personalize resources deployed in your account and shows you how to delete them.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.