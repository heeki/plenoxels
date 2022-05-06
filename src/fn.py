import boto3
import json
import os
from lib.sqs import AdptSQS

# initialization
session = boto3.session.Session()
client = session.client('sqs')
queue_url = os.environ["QUEUE_URL"]
sqs = AdptSQS(session, queue_url)

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
    method = event["httpMethod"]
    body = json.loads(event["body"])
    output = body
    if method == "GET":
        pass
    elif method == "POST":
        sqs.send_message(json.dumps(output))
    response = build_response(200, json.dumps(output))
    return response
