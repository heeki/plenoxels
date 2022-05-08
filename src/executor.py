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

    # handle voxel training
    if command[0] == "/data/svox2/opt/launch_auto.sh":
        response = run_job_training(message)

    # handle validation
    elif command[1] == "/data/svox2/opt/render_imgs.py":
        response = run_job_validation(message)

    return response

def run_job_training(message):
    training_command = message["body"]["command"]
    print("training command {}".format(training_command))
    process = subprocess.Popen(training_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    for line in stdout.splitlines():
        print(line)
    experiment = training_command[1]
    data_dir = training_command[3]
    validation_command = [
        "python",
        "/data/svox2/opt/render_imgs.py",
        "/data/svox2/opt/ckpt/{}/ckpt.npz".format(experiment),
        data_dir
    ]
    message["body"]["command"] = validation_command
    response = run_job_validation(message)
    return response

def run_job_validation(message):
    validation_command = message["body"]["command"]
    print("validation command {}".format(validation_command))
    ckpt_file = validation_command[2]
    if not os.path.exists(ckpt_file):
        response = {
            "error": "ckpt file not found"
        }
        print("failed to process message id: {} (reason: ckpt not found)".format(message["message_id"]))
    else:
        process = subprocess.Popen(validation_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")

        result = {}
        is_final = False
        for line in stdout.splitlines():
            # print(line)
            if line == "AVERAGES":
                is_final = True
                continue
            if is_final:
                print(line)
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
                config_file = "var/{}.json".format(message["message_id"])
                message["body"]["command"].append(config_file)
                with open(config_file, "w") as o:
                    json.dump(message["body"]["config"], o)
                run_job(message)
    except KeyboardInterrupt:
        print("exiting on interrupt")

if __name__ == "__main__":
    main()
