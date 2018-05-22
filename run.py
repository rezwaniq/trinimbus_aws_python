import sys
import boto3
import yaml
from botocore.exceptions import ClientError
import random
import time

#Generating random number to avoid deletion(Remove it in the production)
random_number = str(random.randint(1, 100000))
default_vpc_id = ''
global_input_data = None
dns_name = None
subnets = ''

def getInputData():
    with open("data.yaml", 'r') as stream:
        try:
            input_data = yaml.load(stream)
            global global_input_data
            global_input_data = input_data
            return input_data
        except yaml.YAMLError as exc:
            print(exc)    

def get_vpc_id():
    ec2 = boto3.client('ec2')
    response = ec2.describe_vpcs()
    vpc_list = response.get('Vpcs', [{}])
    

    print('##### Processing VPC #####')
    i = 1
    for vpc in vpc_list:
      is_default = vpc.get('IsDefault', False)
      if is_default:
        print('######VPC Object#####')
        print(vpc)
        print('######VPC Object#####')
        vpc_id = vpc.get('VpcId', '')
        print(vpc_id)
        subnet_response = ec2.describe_subnets(
                        Filters=[
                            {
                                'Name': 'vpc-id',
                                'Values': [
                                    vpc_id,
                                ]
                            },
                        ]
                        
                    )
        subnet_list = subnet_response.get('Subnets', [{}])
        for subnet in subnet_list:
          #print subnet.get('SubnetId', '')
          global subnets
          subnets = subnets + ',' + subnet.get('SubnetId', '')
        
        global default_vpc_id
        default_vpc_id = vpc_id
        print('Selecting default vpc id : ' + default_vpc_id)    
        #global subnets
        subnets = subnets[1:]
        print(subnets)
        return vpc_id   


def create_securitygroup(securit_group_arr, IpPermissions, link_security_group):
    
    ec2 = boto3.client('ec2')
    
    vpc_id = default_vpc_id
    
    try:
        response = ec2.create_security_group(GroupName=securit_group_arr['sec_grp_name'] + random_number,
                                             Description=securit_group_arr['sec_grp_desc'],
                                             VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))                                    
    
        if(link_security_group != ''):
            data = ec2.authorize_security_group_ingress(
                GroupId=security_group_id,
                SourceSecurityGroupName= link_security_group + random_number                   
            )
        else:
            data = ec2.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions= IpPermissions
            )            
             
        print('Ingress Successfully Set %s' % data)
        return security_group_id
    except ClientError as e:
        print(e)    

    
def create_load_balancer():
    ##Creating security grp
    
    input_data = global_input_data
    
    #Creating ssl certificate for load balancer
    certificate_response = create_ssl_certificate('')
    certificate_response_object = certificate_response.get('ServerCertificateMetadata', [{}])
    print('###SSL###')
    print(certificate_response_object)
    certificate_arn = certificate_response_object.get('Arn', '')
    print(certificate_arn)
    print('#####Propogating SSL certificate file######')
    time.sleep(20)
    #'Security Group Permission'
    IpPermissions = [
        {'IpProtocol': 'tcp',
                     'FromPort': 80,
                     'ToPort': 80,
                     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
         {'IpProtocol': 'tcp',
                     'FromPort': 443,
                     'ToPort': 443,
                     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
      
    ]         
    security_grp_id = create_securitygroup(input_data['load_balancer'], IpPermissions, '') 
    
    
    vpc_id = default_vpc_id
    subnet_list = subnets.split(",")
    ## Creating ELB start

    client = boto3.client('elbv2')
    loadbalancerresponse = client.create_load_balancer(
        Name=input_data['load_balancer']['name'] + random_number,
            Subnets=subnet_list,
            
            SecurityGroups=[
                security_grp_id,
            ],
            Scheme=input_data['load_balancer']['scheme'],
            Type=input_data['load_balancer']['type'],
            IpAddressType=input_data['load_balancer']['ipaddresstype']
          
    )
    print('#######LoadBalancer#######')
    print(loadbalancerresponse)
    load_balancer_object = loadbalancerresponse.get('LoadBalancers', [{}])
    
    load_balancer_id = load_balancer_object[0].get('LoadBalancerArn', '')
    global dns_name
    dns_name = load_balancer_object[0].get('DNSName', '')
        
    
    ## Creating ELB ends
    
    load_balancer_target_grp_response = client.create_target_group(
        Name=input_data['target_group']['Name'] + random_number,
        Protocol=input_data['target_group']['Protocol'],
        Port=input_data['target_group']['Port'],
        VpcId= vpc_id,
        HealthCheckProtocol=input_data['target_group']['HealthCheckProtocol'],
        HealthCheckPort=str(input_data['target_group']['HealthCheckPort']),        
        HealthCheckIntervalSeconds=input_data['target_group']['HealthCheckIntervalSeconds'],
        HealthCheckTimeoutSeconds=input_data['target_group']['HealthCheckTimeoutSeconds'],
        HealthyThresholdCount=input_data['target_group']['HealthyThresholdCount'],
        UnhealthyThresholdCount=input_data['target_group']['UnhealthyThresholdCount'],
        Matcher={'HttpCode': str(input_data['target_group']['HttpCode'])},
        TargetType=input_data['target_group']['TargetType']
    )
    print(load_balancer_target_grp_response)
    target_grp_object = load_balancer_target_grp_response.get('TargetGroups', [{}])
    
    target_grp_id = target_grp_object[0].get('TargetGroupArn', '')
    print('Group Id: ' + target_grp_id)
    listner_response = client.create_listener(
        LoadBalancerArn = load_balancer_id,
        Protocol='HTTP',
        Port=80,        
        DefaultActions=[
            {
                'Type': 'forward',
                'TargetGroupArn': target_grp_id
            },
        ]
    )    

    
    https_response = client.create_listener(
        Certificates=[
            {
                'CertificateArn': certificate_arn
            },
        ],
        DefaultActions=[
            {
                'TargetGroupArn': target_grp_id,
                'Type': 'forward',
            },
        ],
        LoadBalancerArn=load_balancer_id,
        Port=443,
        Protocol='HTTPS',
        #SslPolicy='ELBSecurityPolicy-2016-08',
    )
    print('###https response###')
    print(https_response)

    print(listner_response)
    return target_grp_id;
    
def create_autoscalling_launchconfig(target_grp_id):
    client = boto3.client('autoscaling')
    input_data = global_input_data
    #'Security Group Permission'
    IpPermissions = [
        {'IpProtocol': 'tcp',
                     'FromPort': 80,
                     'ToPort': 80,
                     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    ]
    IpPermissions.append({'IpProtocol': 'tcp',
                          'FromPort': 22,
                         'ToPort': 22,
                         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]})      
    security_grp_id = create_securitygroup(input_data['autoscalling_launchconfig'], IpPermissions, '') 
    rds_response = create_rds(security_grp_id)
    print(rds_response)

    rds_host = rds_response.get('DBInstances')[0].get('Endpoint').get('Address')
    rds_user_name = input_data['rds_instance']['MasterUsername']
    rds_user_password=input_data['rds_instance']['MasterUserPassword']
    rds_dbname=input_data['rds_instance']['DBName'] + random_number
    
    print(input_data)
    bash_file = open('bash_script.txt', 'r')
    bash_script = bash_file.read()
    bash_script = bash_script.replace("hostinfo", rds_host)
    bash_script = bash_script.replace("usernameinfo", rds_user_name)
    bash_script = bash_script.replace("passwordinfo", rds_user_password)
    bash_script = bash_script.replace("dbname", rds_dbname)
    launch_config_response = client.create_launch_configuration(
        LaunchConfigurationName=input_data['autoscalling_launchconfig']['LaunchConfigurationName'] + random_number,
        ImageId=input_data['autoscalling_launchconfig']['ImageId'],
        #KeyName=input_data['autoscalling_launchconfig']['KeyName'],
        SecurityGroups=[input_data['autoscalling_launchconfig']['sec_grp_name'] + random_number],
        InstanceType=input_data['autoscalling_launchconfig']['InstanceType'],
        UserData=bash_script,
    )    
    
    auto_scalling_response = client.create_auto_scaling_group(
        AutoScalingGroupName=input_data['autoscalling_launchconfig']['AutoScalingGroupName'] + random_number,
        LaunchConfigurationName=input_data['autoscalling_launchconfig']['LaunchConfigurationName'] + random_number,
        MinSize=input_data['autoscalling_launchconfig']['MinSize'],
        MaxSize=input_data['autoscalling_launchconfig']['MaxSize'],
        DefaultCooldown=input_data['autoscalling_launchconfig']['DefaultCooldown'],
        AvailabilityZones=input_data['autoscalling_launchconfig']['AvailabilityZones'],
        TargetGroupARNs=[target_grp_id],
        HealthCheckType=input_data['autoscalling_launchconfig']['HealthCheckType'],
        HealthCheckGracePeriod=input_data['autoscalling_launchconfig']['HealthCheckGracePeriod'],
        NewInstancesProtectedFromScaleIn=input_data['autoscalling_launchconfig']['NewInstancesProtectedFromScaleIn'],
        
    )
    
    response = client.put_scaling_policy(
        AutoScalingGroupName=input_data['autoscalling_launchconfig']['AutoScalingGroupName'] + random_number,
        PolicyName=input_data['autoscalling_launchconfig']['PolicyName'],
        PolicyType=input_data['autoscalling_launchconfig']['PolicyType'],
        AdjustmentType=input_data['autoscalling_launchconfig']['AdjustmentType'],
        Cooldown=input_data['autoscalling_launchconfig']['Cooldown'],
        EstimatedInstanceWarmup=input_data['autoscalling_launchconfig']['EstimatedInstanceWarmup'],
        TargetTrackingConfiguration={
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': input_data['autoscalling_launchconfig']['PredefinedMetricType'],
                
            },
            'TargetValue': input_data['autoscalling_launchconfig']['TargetValue'],
            'DisableScaleIn': input_data['autoscalling_launchconfig']['DisableScaleIn']
        }
    )    
    return(security_grp_id)

def create_rds(security_group_id):
    input_data = global_input_data
    client = boto3.client('rds')
    #'Security Group Permission'
    IpPermissions = [{'IpProtocol': 'tcp',
                          'FromPort': 3306,
                          'ToPort': 3306,
                          'IpRanges': [{'CidrIp': security_group_id}]
                    }]

    security_grp_id = create_securitygroup(input_data['rds_instance'], IpPermissions, input_data['autoscalling_launchconfig']['sec_grp_name'])     
    response=client.create_db_instance(
        DBName = input_data['rds_instance']['DBName'] + random_number,
        DBInstanceIdentifier=input_data['rds_instance']['DBInstanceIdentifier'] + random_number,
        AllocatedStorage=int(input_data['rds_instance']['AllocatedStorage']),
        DBInstanceClass=input_data['rds_instance']['DBInstanceClass'],
        Engine=input_data['rds_instance']['Engine'],
        MasterUsername=input_data['rds_instance']['MasterUsername'],
        MasterUserPassword=input_data['rds_instance']['MasterUserPassword'],
        VpcSecurityGroupIds=[security_grp_id],
        BackupRetentionPeriod=30,
        Port=3306,
        MultiAZ=False,
        AutoMinorVersionUpgrade=True,
        PubliclyAccessible=False,
        )
    print('###End point###')
    DBInstance = response.get('DBInstance', [{}])
    db_instance_id = DBInstance.get('DBInstanceIdentifier', '')
    print(db_instance_id)
    print('####Processing RDS Instance####')
    sys.stdout.write('Creating.')
    sys.stdout.flush()
    while (True):
      time.sleep(2)
      db_instances = client.describe_db_instances(DBInstanceIdentifier=db_instance_id)
      db_instance_status = db_instances.get('DBInstances')[0].get('DBInstanceStatus')
      if db_instance_status != 'creating':
        return db_instances
      else:
        sys.stdout.write('.')
        sys.stdout.flush()
    print('###End point###')
    return db_instances
 
def create_ssl_certificate(load_balancer):
    client = boto3.client('iam')
    certificate_file = open('my-certificate.pem', 'r') 
    private_file = open('my-private-key.pem', 'r')     
    response = client.upload_server_certificate(
        ServerCertificateName='RezwanCertificate' + random_number,
        CertificateBody = certificate_file.read(),
        PrivateKey = private_file.read(),
    )
    print(response)
    return response
  
input_ch = input("You are about to deploy your infrastructure. Enter 'yes' to continue and 'no' to cancel:")
if input_ch == "yes":
    get_vpc_id()
    getInputData()
    target_grp_id = create_load_balancer()
    security_group_id = create_autoscalling_launchconfig(target_grp_id)
    print(security_group_id)
    print("Program ran without error")
else:
    print("Program exiting")