import boto3
import json
import os
from lib.ddb import AdptDynamoDB
from lib.sqs import AdptSQS

# initialization
session = boto3.session.Session()
queue_url = os.environ["QUEUE_URL"]
table_name = os.environ["TABLE"]
sqs = AdptSQS(session, queue_url)
ddb = AdptDynamoDB(session, table_name)

# helper functions
def build_response(code, body):
    # headers for cors
    headers = {
        # "Access-Control-Allow-Origin": "amazonaws.com",
        # "Access-Control-Allow-Credentials": True,
        "Content-Type": "application/json"
    }
    # lambda proxy integration
    response = {
        "isBase64Encoded": False,
        "statusCode": code,
        "headers": headers,
        "body": body
    }
    return response

def handler(event, context):
    # print(json.dumps(event))
    method = event["httpMethod"]
    if method == "GET":
        scanned = ddb.scan()
        output = []
        for record in scanned:
            cleaned = {k:record[k]["S"] for k in record.keys()}
            output.append(cleaned)
    elif method == "POST":
        body = json.loads(event["body"])
        output = {
            "command": body["command"],
            "config": body["config"]
        }
        response = sqs.send_message(json.dumps(output))
        output["job_id"] = response["MessageId"]
        payload = {
            "job_id": {"S": response["MessageId"]},
            "command": {"S": json.dumps(output["command"])},
            "config": {"S": json.dumps(output["config"])}
        }
        ddb.put(payload)
    response = build_response(200, json.dumps(output))
    return response
