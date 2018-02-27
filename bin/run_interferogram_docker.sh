#!/bin/bash
date
echo "Args: $@"
env
#https://aws.amazon.com/blogs/compute/creating-a-simple-fetch-and-run-aws-batch-job/
echo "Fetch and run interferogram processing"
echo "jobId: $AWS_BATCH_JOB_ID"
echo "jobQueue: $AWS_BATCH_JQ_NAME"
echo "computeEnvironment: $AWS_BATCH_CE_NAME"
echo "interferogram: $INTNAME"
echo "processor: Scott Henderson (scottyh@uw.edu)"
echo "software: ISCE 2.1.0"

# Processing happens here
mkdir $INTNAME
cd /home/ubuntu/$INTNAME
echo $PWD

# Download processing file from s3
aws s3 sync s3://$INTNAME .

# Download S1 SLCs from asf
wget --user=$NASAUSER --password=$NASAPASS --input-file=download-links.txt

# Download aux-cal 20Mb, needed for antenna pattern on old IPF conversions :(
wget -q -r -l2 -nc -nd -np -nH -A SAFE https://s1qc.asf.alaska.edu/aux_cal

# Run ISCE Software
topsApp.py 2>&1 | tee topsApp.log

# Generate web-friendly output and push to s3
isce2aws.py $INTNAME

date
echo "All done!"
