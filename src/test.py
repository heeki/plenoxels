import boto3
import json
import os
from lib.ddb import AdptDynamoDB
from lib.sqs import AdptSQS

# initialization
session = boto3.session.Session(region_name="us-east-2")
client = session.client('sqs')
queue_url = os.environ["QUEUE_URL"]
table_name = os.environ["TABLE"]
sqs = AdptSQS(session, queue_url)
ddb = AdptDynamoDB(session, table_name)

# data
message_id = "6efb8031-43be-4fbb-b3e4-8f0e910d0162"
result = {"psnr": " 34.10292461075813", "ssim": " 0.9748960593342781", "lpips": " 0.02839263891801238"}

# update
item_key = {
    "job_id": {"S": message_id}
}
update_expression = "SET #psnr=:psnr, #ssim=:ssim, #lpips=:lpips"
expression_names = {
    "#psnr": "psnr",
    "#ssim": "ssim",
    "#lpips": "lpips"
}
expression_attributes = {
    ":psnr": {"S": result["psnr"]},
    ":ssim": {"S": result["ssim"]},
    ":lpips": {"S": result["lpips"]}
}
response = ddb.update(item_key, update_expression, expression_names, expression_attributes)
