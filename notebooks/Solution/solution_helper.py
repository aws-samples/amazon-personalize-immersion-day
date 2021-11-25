from pathlib import Path
import json
import ipywidgets as widgets
from IPython.core.display import display, HTML, Markdown
import boto3 
import requests
from time import sleep
from typing import List, Dict, Optional
from multiprocessing import Process
import logging
import re

STACK_NAME = "PersonalizeStack"
INSTANCE_ID = requests.get("http://169.254.169.254/latest/dynamic/instance-identity/document").json()
REGION = INSTANCE_ID["region"]
COMPLETE_STATUS = {"CREATE_COMPLETE", "UPDATE_COMPLETE"}
CREATE_STATUS = {"CREATE_IN_PROGRESS"}
UPDATE_STATUS = {"UPDATE_IN_PROGRESS", "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS"}
RETAIL="Retail"
CPG="CPG"
MEDIA="Media"
DOMAINS = [RETAIL, CPG, MEDIA]
DATASETS={
    domain: {
        "users": str(next(iter(Path(f"/home/ec2-user/SageMaker/amazon-personalize-immersion-day/automation/ml_ops/domain/{domain}/data/Users").glob('*.csv')), "")),
        "items": str(next(iter(Path(f"/home/ec2-user/SageMaker/amazon-personalize-immersion-day/automation/ml_ops/domain/{domain}/data/Items").glob('*.csv')), "")),
        "interactions": str(next(iter(Path(f"/home/ec2-user/SageMaker/amazon-personalize-immersion-day/automation/ml_ops/domain/{domain}/data/Interactions").glob('*.csv')), "")),
        "path": f"train/immersionday/{domain}"
    }
    for domain in DOMAINS
}
CONFIGS={
    domain: (Path(__file__).parent / "config" / f"{domain.lower()}.json").read_bytes()
    for domain in DOMAINS
}


logger = logging.getLogger('SolutionCleanup')
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    

class StopExecution(Exception):
    def __init__(self, msg):
        if msg:
            print(msg)
            
    def _render_traceback_(self):
        pass

    
def exit(msg=None):
    raise StopExecution(msg)
    

def get_aws_account():
    global REGION
    cli = boto3.client("sts", region_name=REGION)
    return cli.get_caller_identity().get("Account")


def show_quick_launch_link():
    global STACK_NAME, REGION
    
    display(HTML(f"""

    <a href="https://{REGION}.console.aws.amazon.com/cloudformation/home?region={REGION}#/stacks/create/review?templateURL=https:%2F%2Fs3.amazonaws.com%2Fsolutions-reference%2Fmaintaining-personalized-experiences-with-machine-learning%2Flatest%2Fmaintaining-personalized-experiences-with-machine-learning.template&stackName={STACK_NAME}">
        <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png" alt="Launch Stack">
    </a>
    """))
    
def get_stack_resource(name, key, output_status=False):
    global STACK_NAME, REGION
    
    cli = boto3.client("cloudformation", region_name=REGION)
    try: 
        stacks = cli.describe_stacks(StackName=STACK_NAME)
    except cli.exceptions.ClientError: 
        print(f"❌ Solution: not ready!")
        print(f"\n\nDid you deploy the stack with the name `{STACK_NAME}` in {REGION}? Make sure the stack is fully deployed and try again.")
        return
    
    stack_status = stacks['Stacks'][0]['StackStatus']
    if stack_status not in COMPLETE_STATUS:
        if output_status:
            print(f"{'Solution':<14}: {stack_status.replace('_',' ').lower().title()}")
        return
    
    resource_name = [output['OutputValue'] for output in stacks['Stacks'][0]['Outputs'] if output['OutputKey'] == key][0]
    if output_status:
        print(f"✅ {'Solution':<14}: {stack_status.replace('_',' ').lower().title()}")

    print(f"✅ {name:<14}: {resource_name}")    
    return resource_name


def wait_for_stack():
    waiter = None
    
    cli = boto3.client("cloudformation", region_name=REGION)
    try: 
        stacks = cli.describe_stacks(StackName=STACK_NAME)
    except cli.exceptions.ClientError: 
        exit(f"❌ Solution: not ready!\n\nDid you deploy the stack with the name `{STACK_NAME}` in {REGION}? Make sure the stack is fully deployed and try again.")
    stack_status = stacks['Stacks'][0]['StackStatus']
    
    if stack_status in CREATE_STATUS:
        print("Stack is creating... Please wait.")
        waiter = cli.get_waiter("stack_create_complete")
    if stack_status in UPDATE_STATUS:
        print("Stack is updating... Please wait.")
        waiter = cli.get_waiter("stack_update_complete")
    if waiter:
        waiter.wait(StackName=STACK_NAME)
        
    cli.update_stack(StackName=STACK_NAME, UsePreviousTemplate=True, Capabilities=["CAPABILITY_IAM"], Tags=[
        {
            "Key": "SOLUTION_VERSION",
            "Value": "v1.1.0"
        },
        {
            "Key": "SOLUTION_ID",
            "Value": "SO0170"
        }
    ])
    waiter = cli.get_waiter("stack_update_complete")
    waiter.wait(StackName=STACK_NAME)


def get_stack_bucket():
    return get_stack_resource("Bucket Name", "PersonalizeBucketName", True)
    
    
def get_stack_dynamo():
    return get_stack_resource("Dynamo Table", "SchedulerTableName")

    
def show_stack_stepfunctions():
    global STACK_NAME, REGION
    
    cli = boto3.client("cloudformation", region_name=REGION)
    paginator = cli.get_paginator('list_stack_resources')
    iterator = paginator.paginate(StackName=STACK_NAME)
    stepfunctions = []
    
    for page in iterator:
        for summary in page['StackResourceSummaries']: 
            if summary['ResourceType'] == "AWS::StepFunctions::StateMachine":
                stepfunctions.append(summary["PhysicalResourceId"])
    
    if stepfunctions:
        md = "# Step Functions:\n\nClick any of the following links to review the step function executions"
        for stepfunction in stepfunctions:
            md += f"\n1. [{stepfunction.rsplit(':', 1)[-1]}](https://console.aws.amazon.com/states/home?region={REGION}#/statemachines/view/{stepfunction})"
        display(Markdown(md))
    
    return stepfunctions
        
            
              
class DatasetUploader:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.dropdown = widgets.Dropdown(options=DOMAINS)
        self.button = widgets.Button(description="Deploy")
        self.output = widgets.Output()
        self.hbox = widgets.HBox([self.dropdown, self.button])
        self.box = widgets.VBox([self.hbox, self.output])
        self.cli = boto3.client('s3')

        self.button.on_click(self.on_button_clicked)
                    
    def on_button_clicked(self, b):
        with self.output:
            b.disabled = True
            self.output.clear_output()
                        
            domain = self.dropdown.value
            print(f"Starting data upload for {domain.lower()} domain to bucket {self.bucket_name}...")
            
            for i in ["interactions", "items", "users"]:            
                file = DATASETS[domain][i]
                key = DATASETS[domain]["path"] + f"/{i}.csv"
                print(f"uploading s3://{self.bucket_name}/{key} ", end='')
                try:
                    self.cli.upload_file(
                        Filename=file,
                        Bucket=self.bucket_name,
                        Key=key
                    )
                    print("... ✅")
                except FileNotFoundError:
                    print("... ❌ (this dataset does not exist for this domain at this time)")
                
            b.disabled = False


class ConfigUploader:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.dropdown = widgets.Dropdown(options=DOMAINS)
        self.show = widgets.Button(description="Show")
        self.deploy = widgets.Button(description="Deploy", button_style="primary", disabled=True)
        self.output = widgets.Textarea(layout={"width": "100%", "height": "auto"}, placeholder="You must show/ review the configuration before deployment", rows=10)
        
        self.form_rows = [
            widgets.HBox([
                self.dropdown, self.show, self.deploy
            ]),
            widgets.HBox([
                self.output,                   
            ]),
        ]
        self.setup_form()
        self.cli = boto3.client('s3')

        self.show.on_click(self.on_click_show)
        self.deploy.on_click(self.on_click_deploy)
        self.dropdown.observe(self.on_change)
    
    def setup_form(self):
        self.form = widgets.VBox(self.form_rows)
    
    def on_change(self, change):
        if not (change['type'] == 'change' and change['name'] == 'value'):
            return 
        
        self.output.value = ""
        self.show.description = "Show"
        self.deploy.disabled = True
        
    def clear_output(self):
        self.output.value = ""
    
    def on_click_show(self, b):
        if self.show.description == "Show":
            self.clear_output()
            domain = self.dropdown.value
            self.output.value = CONFIGS[domain]
            self.deploy.disabled = False
            self.show.description = "Hide"
        else: 
            self.output.value = ""
            self.deploy.disabled = True
            self.show.description = "Show"
        
    def on_click_deploy(self, b):
        self.clear_output()
        b.disabled = True

        domain = self.dropdown.value
        self.output.value += f"Starting config upload for {domain.lower()} domain to bucket {self.bucket_name}...\n"

        key = f"train/immersionday/{domain}/config.json"
        self.output.value += f"uploading s3://{self.bucket_name}/{key} "
        try:
            self.cli.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=CONFIGS[domain]
            )
            self.output.value += "... ✅\n"
        except FileNotFoundError:
             self.output.value += "... ❌ (this dataset does not exist for this domain at this time)\n"

            
def show_dataset_uploader(bucket_name):
    uploader = DatasetUploader(bucket_name)
    display(uploader.box)
    

def show_config_uploader(bucket_name):
    uploader = ConfigUploader(bucket_name)
    display(uploader.form)
    
    
def camel_to_snake(s):
    """
    Convert a camelCasedName to a snake_cased_name
    :param s: the camelCasedName
    :return: the snake_cased_name
    """
    return "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip("_")


def snake_to_camel(s: str):
    """
    Convert a snake_cased_name to a camelCasedName
    :param s: the snake_cased_name
    :return: camelCasedName
    """
    components = s.split("_")
    return components[0] + "".join(y.title() for y in components[1:])


def camel_to_dash(s: str):
    """
    Convert a camelCasedName to a dash-cased-name
    :param s: the camelCasedName
    :return: the dash-cased-name
    """
    return "".join(["-" + c.lower() if c.isupper() else c for c in s]).lstrip("-")
    
class ResourceName:
    def __init__(self, name: str):
        self.name = self._validated_name(name)

    def _validated_name(self, name) -> str:
        """
        Validate that a name is valid, raising ValueError if it is not
        :param name: the name to validate
        :return: the validated name
        """
        if not name.isalpha():
            raise ValueError("name must be camelCased")
        if not name[0].islower():
            raise ValueError("name must start with a lower case character")
        return name

    @property
    def dash(self) -> str:
        """
        Get the dash-cased-name of the resource
        :return: the dash-cased-name
        """
        return camel_to_dash(self.name)

    @property
    def snake(self) -> str:
        """
        Get the snake_cased_name of the resource
        :return: the snake_cased_name
        """
        return camel_to_snake(self.name)

    @property
    def camel(self) -> str:
        """
        Get the camelCasedName of the resource
        :return: the camelCasedName
        """
        return self.name


    
class Resource:
    children = []
    has_soft_limit: bool = False
    removable = False

    def __init__(self):
        name = self.__class__.__name__
        name = name[0].lower() + name[1:]
        self.name = ResourceName(name)
    
    
class BatchInferenceJob(Resource):
    pass

class Campaign(Resource):
    removable = True

class DatasetImportJob(Resource):
    pass    

class EventTracker(Resource):
    removable = True

class Filter(Resource):
    removable = True    
    
class Schema(Resource):
    removable = True   
    
class Dataset(Resource):
    children = [DatasetImportJob()]
    removable = True

class SolutionVersion(Resource):
    children = [BatchInferenceJob()]
    has_soft_limit = True       
    
class Solution(Resource):
    children = [Campaign(), SolutionVersion()]
    removable = True        
    
class DatasetGroup(Resource):
    children = [Dataset(), Filter(), Solution(), EventTracker()]
    removable = True 
    
    
def get_resource_from_arn(arn: str) -> Resource:
    if re.match(r"^arn:.*:personalize:.*:\d{12}:dataset-group/.+$", arn):
        return DatasetGroup()
    elif re.match(r"^arn:.*:personalize:.*:\d{12}:dataset/.+/(USERS|INTERACTIONS|ITEMS)$", arn):
        return Dataset()
    elif re.match(r"^arn:.*:personalize:.*:\d{12}:event-tracker/.+$", arn):
        return EventTracker()
    elif re.match(r"^arn:.*:personalize:.*:\d{12}:campaign/.+$", arn):
        return Campaign()
    elif re.match(r"^arn:.*:personalize:.*:\d{12}:filter/.+$", arn):
        return Filter()
    elif re.match(r"^arn:.*:personalize:.*:\d{12}:solution/[^:]+$", arn):
        return Solution()
    elif re.match(r"^arn:.*:personalize:.*:\d{12}:solution/[^:]+:.*$", arn):
        return SolutionVersion()
    elif re.match(r"^arn:.*:personalize:.*:\d{12}:schema/.+$", arn):
        return Schema()
    elif re.match(r"^arn:.*:personalize:.*:\d{12}:batch-inference-job/.+$", arn):
        return BatchInferenceJob()
    elif re.match(r"^arn:.*:personalize:.*:\d{12}:dataset-import-job/.+$", arn):
        return DatasetImportJob()
    else:
        raise ValueError(f"unsupported ARN {arn}")
        

    
def delete_resource(region: str, arn: str):
    """Intended to be used as part of a multiprocessing delete."""
    resource = get_resource_from_arn(arn)

    logger.info(f"{arn} delete requested")
    if not resource.removable:
        logger.info(f"{arn} is not removable (service does not allow delete)")
        return

    cli = boto3.client("personalize", region_name=region)
    deleted = False
    delete_fn_name = f"delete_{resource.name.snake}"
    delete_fn = getattr(cli, delete_fn_name)

    while not deleted:
        try:
            delete_fn(**{
                f"{resource.name.camel}Arn": arn
            })
            logger.info(f"{arn} delete triggered")
        except cli.exceptions.ResourceInUseException as exc:  # resource is deleting
            logger.debug(f"{arn} delete not available: {str(exc)}")
        except cli.exceptions.ResourceNotFoundException:
            logger.info(f"{arn} deleted")
            deleted = True
        sleep(10)
        
        
class Personalize:
    def __init__(self):
        global REGION
        self.cli = boto3.client('personalize', region_name=REGION)

    @property
    def exceptions(self):
        return self.cli.exceptions

    def list(self, resource: Resource, filters: Optional[Dict] = None):
        if not filters:
            filters = {}
        list_fn_name = f"list_{resource.name.snake}s"
        paginator = self.cli.get_paginator(list_fn_name)
        iterator = paginator.paginate(**filters)
        for page in iterator:
            resource_key = [
                k
                for k in list(page.keys())
                if k not in ("ResponseMetadata", "nextToken")
            ].pop()
            for item in page[resource_key]:
                yield item


class ServiceModel:
    """Lists all resources in Amazon Personalize for lookup against the dataset group ARN"""

    def __init__(self):
        global REGION
        self.cli = Personalize()
        self.region_name = REGION
        self._arn_ownership = {}

        self.dataset_groups = self._arns(self.cli.list(DatasetGroup()))
        for dataset_group in self.dataset_groups:
            logger.debug(f"listing children of {dataset_group}")
            self._list_children(DatasetGroup(), dataset_group, dataset_group)

    def all_owned_by(self, dataset_group_owner: str) -> List[str]:
        if not dataset_group_owner.startswith("arn:"):
            dataset_group_owner = f"arn:aws:personalize:{self.region_name}:{get_aws_account()}:dataset-group/{dataset_group_owner}"

        return [k for k, v in self._arn_ownership.items() if v == dataset_group_owner]
    
    def delete_all_owned_by(self, *dataset_group_owner: str):
        owned_by = []
        for dsg in dataset_group_owner: 
            owned_by.extend(self.all_owned_by(dsg))
            owned_by.append(f"arn:aws:personalize:{self.region_name}:{get_aws_account()}:dataset-group/{dsg}")
        owned_by = list(set(owned_by))

        jobs = []
        for arn in owned_by:
            job = Process(target=delete_resource, args=(self.region_name, arn))
            jobs.append(job)
            job.start()

        for job in jobs:
            job.join()

    def owned_by(self, resource_arn, dataset_group_owner: str) -> bool:
        """
        Check
        :param resource_arn: the resource ARN or name to check
        :param dataset_group_owner: the dataset group owner expected
        :return: True if the resource is managed by the dataset group, otherwise False
        """
        if not dataset_group_owner.startswith("arn:"):
            dataset_group_owner = f"arn:aws:personalize:{self.region_name}:{get_aws_account()}:dataset-group/{dataset_group_owner}"

        return dataset_group_owner == self._arn_ownership.get(resource_arn, False)

    def available(self, resource_arn: str) -> bool:
        """
        Check if the requested ARN is available
        :param resource_arn: requested ARN
        :return: True if the ARN is available, otherwise False
        """
        all_arns = set(self._arn_ownership.keys()).union(
            set(self._arn_ownership.values())
        )
        return resource_arn not in all_arns

    def _list_children(self, parent: Resource, parent_arn, dsg: str) -> None:
        """
        Recursively list the children of a resource
        :param parent: the parent Resource
        :param parent_arn: the parent Resource ARN
        :param dsg: the parent dataset group ARN
        :return: None
        """
        for c in parent.children:
            child_arns = self._arns(
                self.cli.list(c, filters={f"{parent.name.camel}Arn": parent_arn})
            )

            for arn in child_arns:
                self._arn_ownership[arn] = dsg
                self._list_children(c, arn, dsg)

    def _arns(self, l: List[Dict]) -> List[str]:
        """
        Lists the first ARN found for each resource in a list of resources
        :param l: the list of resources
        :return: the list of ARNs
        """
        return [
            [v for k, v in resource.items() if k.endswith("Arn")][0] for resource in l
        ]

    
def delete_personalize_resources():
    global REGION
    personalize = ServiceModel()
    personalize.delete_all_owned_by("immersion_day_retail", "immersion_day_cpg", "immersion_day_media")
