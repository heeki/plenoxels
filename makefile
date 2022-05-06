include etc/environment.sh

infra: infra.package infra.deploy
infra.package:
	sam package -t ${INFRA_TEMPLATE} --region ${REGION} --output-template-file ${INFRA_OUTPUT} --s3-bucket ${S3BUCKET}
infra.deploy:
	sam deploy -t ${INFRA_OUTPUT} --region ${REGION} --stack-name ${INFRA_STACK} --parameter-overrides ${INFRA_PARAMS} --capabilities CAPABILITY_NAMED_IAM

ec2: ec2.package ec2.deploy
ec2.package:
	sam package -t ${EC2_TEMPLATE} --region ${REGION} --output-template-file ${EC2_OUTPUT} --s3-bucket ${S3BUCKET}
ec2.deploy:
	sam deploy -t ${EC2_OUTPUT} --region ${REGION} --stack-name ${EC2_STACK} --parameter-overrides ${EC2_PARAMS} --capabilities CAPABILITY_NAMED_IAM

apigw: apigw.package apigw.deploy
apigw.package:
	sam package -t ${APIGW_TEMPLATE} --region ${REGION} --output-template-file ${APIGW_OUTPUT} --s3-bucket ${S3BUCKET}
apigw.deploy:
	sam deploy -t ${APIGW_OUTPUT} --region ${REGION} --stack-name ${APIGW_STACK} --parameter-overrides ${APIGW_PARAMS} --capabilities CAPABILITY_NAMED_IAM

sam.local.api:
	sam local start-api -t ${APIGW_TEMPLATE} --parameter-overrides ${APIGW_PARAMS} --env-vars etc/envvars.json
sam.local.invoke:
	sam local invoke -t ${APIGW_TEMPLATE} --parameter-overrides ${APIGW_PARAMS} --env-vars etc/envvars.json -e etc/event.json Fn | jq
