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
    command = message["body"]["command"]
    print("executing command {}".format(command))
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    # handle voxel training
    if command[0] == "/data/svox2/opt/launch.sh":
        pass

    # handle validation
    elif command[1] == "/data/svox2/opt/render_imgs.py":
        result = {}
        is_final = False
        for line in stdout.splitlines():
            # print(line)
            if line == "AVERAGES":
                is_final = True
                continue
            if is_final:
                fields = line.split(":")
                result[fields[0].lower()] = fields[1]
        print(json.dumps(result))

        # psnr = peak signal to noise ratio
        # ssim = structural similarity index measure
        # lpips = learned perceptual image patch similarity
        item_key = {
            "job_id": {"S": message["message_id"]}
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
