# Implementing Plenoxels on AWS
## Overview
The source repository (https://github.com/sxyu/svox2) and original implementation provides a mechanism for a parallel task executor to schedule many tasks on a single machine. This repository aims to investigate the feasibility of leveraging the scale-out resources of AWS to increase parallel processing for running the Plenoxels implementation.

## Setup
This repository uses the AWS CLI and the AWS Serverless Application Model (SAM) for conducting deployments into AWS. The AWS CLI should be installed using the followig [documentation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-version.html). The SAM CLI should be installed using the following [documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html).

## Deployment
Make directives are provided for implementing this repository. In order to execute the make directives, the `environment.template` configuration file needs to be copied to `environment.sh` and updated with your configuration information.

The following are configuration parameters for performing deployments with AWS SAM.

* `S3BUCKET`: The S3 bucket that is used by the `sam package` directive for artifacts.
* `PROFILE`: Your AWS CLI configuration profile.

The following are configuration parameters for deploying supporting infrastructure.

* `P_NAME`: A temporary placeholder for now.
* `INFRA_STACK`: The name of the CloudFormation stack.
* `INFRA_TEMPLATE`: Path to the CloudFormation template, leave this as is.
* `INFRA_OUTPUT`: Path to the SAM output template, leave this as is.
* `INFRA_PARAMS`: Parameters for the CloudFormation stack, leave this as is.
* `O_BUCKET`: The name of the S3 bucket, output from the CloudFormation stack deployment.
* `O_QUEUE_URL`: The URL of the SQS queue, output from the CloudFormation stack deployment.
* `O_QUEUE_ARN`: The ARN of the SQS queue, output from the CloudFormation stack deployment.
* `O_TABLE_ARN`: The ARN of the DynamoDB table, output from the CloudFormation stack deployment.

To deploy the infrastructure stack, run `make infra`.

The following are configuration parameters for deploying the EC2 infrastructure.

* `P_VPC_ID`: VPC identifier where your EC2 instance will be deployed
* `P_SUBNET_IDS`: A comma-separated list of subnet ids
* `P_INGRESS_CIDR`: Allowed CIDR range for ingress to the instance
* `P_IMAGE_ID`: Deep Learning AMI for GPU CUDA 11.4.3 on Amazon Linux 2, leave as is
* `P_INSTANCE_TYPE`: GPU instance type, leave as is
* `P_SUBNET_SELECTION`: Index to select within the subnet id list
* `P_SSH_KEY`: The name of the EC2 SSH key
* `EC2_STACK`: The name of the CloudFormation stack
* `EC2_TEMPLATE`: Path to the CloudFormation template, leave this as is.
* `EC2_OUTPUT`: Path to the SAM output template, leave this as is.
* `EC2_PARAMS`: Parameters for the CloudFormation stack, leave this as is.
* `O_EC2`: The FQDN of the EC2 instance, output from the CloudFormation stack deployment.

To deploy the infrastructure stack, run `make ec2`.

The following are configuration parameters for deploying the API infrastructure.

* `P_API_STAGE`: The API stage name for the deployment.
* `P_FN_MEMORY`: The amount of memory to allocate to the Lambda function.
* `P_FN_TIMEOUT`: The timeout (in seconds) for the Lambda function.

To deploy the api stack, run `make apigw`.

## Setting up the Job Executor
The job executor setup is not yet automated (WIP). To set it up on the EC2 instances, clone this repository and perform the following steps.

```bash
cp src/launch_auto.sh /data/svox2/opt
```

## Running the Job Executor
The job executor depends on two environment variables for reading from SQS and writing outputs to DynamoDB.

```bash
export REGION=your-region, e.g. us-east-2
export QUEUE_URL=your-https-queue-url, e.g. https://sqs.[your-region].amazonaws.com/[your-account-id]/[your-queue-name]
export TABLE=your-dynamodb-table-name
python src/executor.py
```

## Submitting a Job
Jobs are submitted via API infrastructure. The job submissions can be executed as follows:

```bash
curl -s -XPOST -d @etc/job_training_drums.json https://[your-api-id].execute-api.[your-region].amazonaws.com/dev/ | jq
```

where @etc/job_training_drums.json takes the following form. Additional examples of job submission files are included in the etc directory.

```json
{
    "command": [
        "/data/svox2/opt/launch_auto.sh",
        "test_synthetic_drums",
        "00:1e.0",
        "/data/nerf_synthetic/drums",
        "-c"
    ],
    "config": {
        "reso": "[[256, 256, 256], [512, 512, 512]]",
        "upsamp_every": 38400,
        "lr_sigma": 3e1,
        "lr_sh": 1e-2,
        "lambda_tv": 1e-5,
        "lambda_tv_sh": 1e-3
    }
}
```

Jobs are queried via API infrastructure. That query can be executed as follows:

```bash
curl -s -XGET https://[your-api-id].execute-api.[your-region].amazonaws.com/dev/ | jq
```
