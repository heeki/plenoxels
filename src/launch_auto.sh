#!/bin/bash

echo Launching experiment $1
echo GPU $2
echo EXTRA ${@:3}

CKPT_DIR=/data/svox2/opt/ckpt/$1
mkdir -p $CKPT_DIR
NOHUP_FILE=$CKPT_DIR/log
echo CKPT $CKPT_DIR
echo LOGFILE $NOHUP_FILE

CUDA_VISIBLE_DEVICES=$2 python -u /data/svox2/opt/opt.py -t $CKPT_DIR ${@:3} | tee $NOHUP_FILE 2>&1