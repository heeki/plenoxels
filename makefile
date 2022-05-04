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
