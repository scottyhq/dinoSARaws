#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process multiple interferograms via AWS Batch (Spot Market)

# EXAMPLE:
# discover path name for area of interest (3 sisters volcano)
get_asf_inventory.py -r 44.0 44.5 -122.0 -121.5
# process 3 interferograms (master=20170927 with 3 preceding dates)
# NOTE: this will run topsApp.py for subswath 2, and region of interest defined by search
proc_batch_master.py -p 115 -m 20170927 -s 3 -n 2 -r 44.0 44.5 -122.0 -121.5 -g 44.0 44.5 -122.0 -121.5

@modified: 12/08/2017
@author: scott
"""

import argparse
import os
import geopandas as gpd
import boto3

def cmdLineParse():
    '''
    Command line parser.
    '''
    parser = argparse.ArgumentParser( description='prepare ISCE 2.1 topsApp.py')
    parser.add_argument('-m', type=str, dest='master', required=True,
            help='Master date')
    parser.add_argument('-s', type=int, dest='slave', required=True,
            help='Number of slaves')
    parser.add_argument('-p', type=int, dest='path', required=True,
            help='Path/Track/RelativeOrbit Number')
    parser.add_argument('-n', type=int, nargs='+', dest='swaths', required=False,
	        default=[1,2,3], choices=(1,2,3),
            help='Subswath numbers to process')
    parser.add_argument('-r', type=float, nargs=4, dest='roi', required=False,
            metavar=('S','N','W','E'),
	        help='Region of interest bbox [S,N,W,E]')
    parser.add_argument('-g', type=float, nargs=4, dest='gbox', required=False,
            metavar=('S','N','W','E'),
	        help='Geocode bbox [S,N,W,E]')

    return parser.parse_args()


def get_pairs(inps):
    ''' 
    Load geojson inventory, find preceding pairs to interfere with master date
    '''
    # NOTE: should test here for something like 50% overlap (to avoid situations where
    # S1A & S1B don't actually overlap despite being in same ROI,,,
    

def create_s3buckets(inps,slaveList):
    '''
    Create S3 buckets for given master
    '''

    s3 = boto3.resource('s3')
    for slave in slaveList:
        bucketName = 'int-{0}-{1}'.format(inps.master, slave)
        s3.create_bucket(bucketName)
        bashFile = write_bash_script(inps.master, slave)
        s3.upload_file(bashFile, bucketName, bashFile)


def write_bash_script(inps, slave)
    filename = 'proc-{master}-{slave}.sh'.format(**vars(inps))
    with open(filename, 'w') as txt:
        txt.write('''#!/bin/bash
# Make directories for processing - already in AMI
cd /mnt/data
mkdir dems poeorb auxcal
# Get the latest python scripts from github & add to path
git clone https://github.com/scottyhq/dinoSAR.git
export PATH=/mnt/data/dinoSAR/bin:$PATH
# Prepare interferogram directory
prep_topsApp.py -i query.geojson -p {path} -m {master} -s {slave} -n {swaths} -r {roi} -g {gbox}
# Run code
cd int-{master}-{slave}
topsApp.py 2>&1 | tee topsApp.log
cp *xml *log merged
aws s3 sync merged/ s3://int-{master}-{slave}/ 
# Send email
aws sns publish --topic-arn "arn:aws:sns:us-west-2:295426338758:email-me" --message file://topsApp.log --subject "int-{master}-{slave} Finished"
'''.format(**vars(inps)))

        return filename


def launch_batch():
    '''
    submit AWS Batch Job
    '''
    cmd = 'aws batch submit-job --job-name example --job-queue HighPriority  --job-definition sleep60'.format(name,template)
    print(cmd)
    #os.system(cmd)


if __name__ == '__main__':
    inps = cmdLineParse()
    inps.roi = ' '.join([str(x) for x in inps.roi])
    inps.gbox = ' '.join([str(x) for x in inps.gbox])
    inps.swaths = ' '.join([str(x) for x in inps.swaths])

    template = create_cloudformation_script(inps)
    print('Running Interferogram on EC2')
    #launch_stack(template)
    print('EC2 should close automatically when finished...')
