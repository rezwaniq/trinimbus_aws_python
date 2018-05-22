# Project Title

This Python Code and Cloud Formation template has been written to auto deploy an infrastructure and a web application on top of that. Although Cloud Formation template is deploying the complete stack and downloading files from Git, however I could not troubleshoot the database connection page due to shortage of time.
The code and template will deploy EC2 instances in an Auto Scalling group which will be fronted by ELBv2. Behind the EC2s there is MySQL DB running. Using the DNS string of the ELB you can access the PHP web application which is talking to the DB instance. 

### Prerequisites

Following prerequisites have to be ensured.
1. AWS account with correct quota.
2. AWS account API key and password.
3. [Python](https://www.python.org/downloads/) installation with [Boto3](https://boto3.readthedocs.io/) library.
4. Put API access key and password in the 'credential' file in the path below,
For Windows machine- \Users\eiqbmuh\.aws
For MAC - ~/.aws

Example:
[default]

aws_access_key_id = AKIAJ5xxxxxxT76DPxxx

aws_secret_access_key = xqiBCxxxis1tufDQGYTd/Vwq2Bf/xxxxxxxxxxU1

### Installing

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

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
