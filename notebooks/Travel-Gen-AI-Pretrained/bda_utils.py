import json
import time
import boto3
import botocore
import botocore.exceptions
from typing import Optional

s3 = boto3.client('s3')
bda = boto3.client('bedrock-data-automation')

def get_bda_project_arn(project_name: str) -> Optional[str]:
    response = bda.list_data_automation_projects(projectStageFilter="LIVE")
    projects = response["projects"]

    project_arn = None
    for project in projects:
        if project["projectName"] == project_name:
            project_arn = project["projectArn"]
            break

    return project_arn
    
def create_bda_project(project_name: str, project_description: str):

    try:
        response = bda.create_data_automation_project(
            projectName=project_name,
            projectDescription=project_description,
            standardOutputConfiguration={
                "audio": {
                    "extraction": {
                        "category": {"state": "ENABLED", "types": ["TRANSCRIPT"]}
                    },
                    "generativeField": {"state": "DISABLED", "types": []},
                },
                "video": {
                    "extraction": {
                        "category": {"state": "ENABLED", "types": ["CONTENT_MODERATION"]},
                        "boundingBox": {"state": "DISABLED"},
                    },
                    "generativeField": {"state": "ENABLED", "types": ["VIDEO_SUMMARY"]}
                },
                "image": {
                    "extraction": {
                        "category": {"state": "ENABLED", "types": ["CONTENT_MODERATION"]},
                        "boundingBox": {"state": "DISABLED"},
                    },
                    "generativeField": {"state": "ENABLED", "types": ["IMAGE_SUMMARY"]},
                },
                "document": {
                    "extraction": {
                        "granularity": {"types": ["PAGE", "ELEMENT"]},
                        "boundingBox": {"state": "DISABLED"},
                    },
                    "generativeField": {"state": "DISABLED"},
                    "outputFormat": {
                        "textFormat": {"types": ["MARKDOWN", "HTML"]},
                        "additionalFileFormat": {"state": "DISABLED"},
                    },
                },
            },
            customOutputConfiguration={"blueprints": []},
        )
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ConflictException":
            print("Using existing Data Automation project")
            return get_bda_project_arn(project_name)
        else:
            raise e

    project_arn = response["projectArn"]
    creation_status = response["status"]

    max_wait_time = 60
    while creation_status == "IN_PROGRESS":
        creation_status = bda.get_data_automation_project(
            projectArn=project_arn
        )["project"]["status"]

        print(f"Project creation status: {creation_status}")
        time.sleep(5)
        max_wait_time -= 5

        if max_wait_time <= 0:
            raise TimeoutError("Project creation took too long")

    if creation_status == "COMPLETED":
        return project_arn
    else:
        raise Exception(f"Project creation failed with status: {creation_status}")
def get_json_object_from_s3_uri(s3_uri) -> dict:
    s3_uri_split = s3_uri.split('/')
    bucket = s3_uri_split[2]
    key = '/'.join(s3_uri_split[3:])
    object_content = s3.get_object(Bucket=bucket, Key=key)['Body'].read()
    return json.loads(object_content)