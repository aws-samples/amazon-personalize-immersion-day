import sys
import getopt
import logging
import botocore
import boto3
import time
from packaging import version
from time import sleep
from botocore.exceptions import ClientError

logger = logging.getLogger()
personalize = None

filter_arns = []
dataset_arns = []
schema_arns = []
event_tracker_arns = []
campaign_arns = []
solution_arns = []

def _get_dataset_group_arn(dataset_group_name):
    dsg_arn = None

    paginator = personalize.get_paginator('list_dataset_groups')
    for paginate_result in paginator.paginate():
        for dataset_group in paginate_result["datasetGroups"]:
            if dataset_group['name'] == dataset_group_name:
                dsg_arn = dataset_group['datasetGroupArn']
                break

        if dsg_arn:
            break

    if not dsg_arn:
        raise NameError(f'Dataset Group "{dataset_group_name}" does not exist; verify region is correct')

    return dsg_arn

def _get_solutions(dataset_group_arn):
    paginator = personalize.get_paginator('list_solutions')
    for paginate_result in paginator.paginate(datasetGroupArn = dataset_group_arn):
        for solution in paginate_result['solutions']:
            print(solution['solutionArn'])
            solution_arns.append(solution['solutionArn'])
    return solution_arns


def _get_campaigns(solution_arns):
    for solution_arn in solution_arns:
        paginator = personalize.get_paginator('list_campaigns')
        for paginate_result in paginator.paginate(solutionArn = solution_arn):
            for campaign in paginate_result['campaigns']:
                campaign_arns.append(campaign['campaignArn'])
                



def _get_event_trackers(dataset_group_arn):
    event_trackers_paginator = personalize.get_paginator('list_event_trackers')
    for event_tracker_page in event_trackers_paginator.paginate(datasetGroupArn = dataset_group_arn):
        for event_tracker in event_tracker_page['eventTrackers']:
            event_tracker_arns.append(event_tracker['eventTrackerArn'])


def _get_filters(dataset_group_arn):
    filters_response = personalize.list_filters(datasetGroupArn = dataset_group_arn, maxResults = 100)
    for filter in filters_response['Filters']:
        filter_arns.append(filter['filterArn'])

        
def _get_datasets_and_schemas(dataset_group_arn):
    dataset_paginator = personalize.get_paginator('list_datasets')
    for dataset_page in dataset_paginator.paginate(datasetGroupArn = dataset_group_arn):
        for dataset in dataset_page['datasets']:
            describe_response = personalize.describe_dataset(datasetArn = dataset['datasetArn'])
            schema_arns.append(describe_response['dataset']['schemaArn'])
            dataset_arns.append(dataset['datasetArn'])


def get_dataset_group_info(dataset_group_name, region = None):  
    global personalize
    personalize = boto3.client(service_name = 'personalize', region_name = region)
    dataset_group_arn = _get_dataset_group_arn(dataset_group_name)
    logger.info('Dataset Group ARN: ' + dataset_group_arn)
    # get soltions    
    _get_solutions(dataset_group_arn)
    # 1. get campaigns
    _get_campaigns(solution_arns)
    
    # 3. Get event trackers
    _get_event_trackers(dataset_group_arn)

    # 4. Get filters
    _get_filters(dataset_group_arn)

    # 5. Get datasets and their schemas
    _get_datasets_and_schemas(dataset_group_arn)
    
    

    
    return dataset_group_arn

