# Project Title

This Python Code and Cloud Formation template has been written to auto deploy an infrastructure and a web application on top of that. Although Cloud Formation template is deploying the complete stack and downloading files from Git, however I could not troubleshoot the database connection page due to shortage of time.
The code and template will deploy EC2 instances in an Auto Scalling group which will be fronted by ELBv2. Behind the EC2s there is MySQL DB running. Using the DNS string of the ELB you can access the PHP web application which is talking to the DB instance. 

### Prerequisites

Following prerequisites have to be ensured before doing automated infrastructure services and application deployment via Python code,
1. AWS account with correct quota and access to default VPC.
2. AWS account API key and password.
3. [Python](https://www.python.org/downloads/) installation with [Boto3](https://boto3.readthedocs.io/) library.
4. Put API access key and password in the 'credential' file in the path below,
For Windows machine- \Users\eiqbmuh\.aws
For MAC - ~/.aws
```
Example:
[default]
aws_access_key_id = AKIAJ5xxxxxxT76DPxxx
aws_secret_access_key = xqiBCxxxis1tufDQGYTd/Vwq2Bf/xxxxxxxxxxU1
```

Following prerequisites have to be ensured before doing automated infrastructure services and application deployment via Cloud Formation,
1. AWS account with correct quota and access to default VPC.

### Installing

For infrastructure services and application deployment via Python code,

1. You need to update the data.yaml file according to your needs. 
2. Pay special attention to filling out AvailabilityZones info as this needs to have the list of availibility zones from your default VPC where you want your EC2 Auto Scalling to launch the instances. You do not have to provide all theAvailabilityZones. Just provide the ones where you want your EC2s to be launched. Python code will automatically take whatever you put in here.
```
AvailabilityZones: 
        - us-east-1a
        - us-east-1b
        - us-east-1c
```
3. Self signed certificate file will be uploaded to AMI. Change it if necessary.
4. Random number will be added in order to avoid duplication error and save time. Remove it if necessage.
5. You can rerun run.py without deleting old instances(EC2, RDS etc)


For infrastructure services and application deployment via Cloud Formation,

1. You need access to CloudFormation_Deployment_Template_Lamp.txt.
2. From AWS Management Console, goto Cloud Formation service.
3. Click 'Create Stack' and upload the above mentioned template.
4. Enter the relevant details and then click 'create'.

