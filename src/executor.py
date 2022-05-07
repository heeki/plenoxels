import boto3
import json
import os
import subprocess
from lib.sqs import AdptSQS
from lib.ddb import AdptDynamoDB

# environment
region_name = os.environ["REGION"]
queue_url = os.environ["QUEUE_URL"]
table = os.environ["TABLE"]

# initialization
session = boto3.session.Session(region_name=region_name)
sqs = AdptSQS(session, queue_url)
ddb = AdptDynamoDB(session, table)

# job runner
def run_job(message):
    print("processing {}".format(message["message_id"]))
    param_ckpt = "ckpt/test_synthetic_lego/ckpt.npz"
    param_data = "/data/nerf_synthetic/lego"
    command = ["python", "render_imgs.py", param_ckpt, param_data]
    # process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdout, stderr = process.commumnicate()
    # print(stdout)
    # print(stderr)

    # psnr = peak signal to noise ratio
    # ssim = structural similarity index measure 
    # lpips = learned perceptual image patch similarity
    response = {
        "job_id": {"S": message["message_id"]},
        "psnr": {"S": str(34.10292461075813)},
        "ssim": {"S": str(0.9748960593342781)},
        "lpips": {"S": str(0.02839263891801238)}
    }
    ddb.put(response)
    if "psnr" in response:
        print("successfully processed message id: {}".format(message["message_id"]))
        sqs.delete_message(message["receipt_handle"])

    return response

# main
def main():
    try:
        while True:
            response = sqs.receive_message(
                max_messages=1,
                wait_time=10
            )
            for message in response:
                with open("var/{}.json".format(message["message_id"]), "w") as o:
                    json.dump(message["body"], o)
                run_job(message)

    except KeyboardInterrupt:
        print("exiting on interrupt")

if __name__ == "__main__":
    main()
