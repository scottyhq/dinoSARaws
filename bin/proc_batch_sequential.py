#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process all adjacent interferograms for a particular region of interest.


EXAMPLE:
For example, a query.geojson with the following scenes:
...
20170927
20170915
20170903
20170812
...

proc_batch_sequential.py -p 115 -n 2 -r 44.0 44.5 -122.0 -121.5 -g 44.0 44.5 -122.0 -121.5

# this will run topsApp.py for subswath 2, and region of interest defined by search
# for the following pairs:
int-20170927-20170915
int-20170915-20170903
int-20170903-20170812

@author: scott
"""

import argparse
import os

def cmdLineParse():
    '''
    Command line parser.
    '''
    parser = argparse.ArgumentParser( description='prepare ISCE 2.1 topsApp.py')
    parser.add_argument('-m', type=str, dest='main', required=True,
            help='Main date')
    parser.add_argument('-s', type=str, dest='subordinate', required=True,
            help='Subordinate date')
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



def create_cloudformation_script(inps):
    '''
    Write YML file to process and interferogram based on user input
    NOTE: could probably do this better w/ JSON tools...
    '''
    filename = 'proc-{main}-{subordinate}.yml'.format(**vars(inps))
    with open(filename, 'w') as yml:
        yml.write('''AWSTemplateFormatVersion: "2010-09-09"
Description: "CloudFormation template to create interferogram: int-{main}-{subordinate}"
Resources:
  MyEC2Instance:
    Type: "AWS::EC2::Instance"
    Properties: 
      ImageId: "ami-8deb36f5"
      InstanceType: "{instance}"
      KeyName: "isce-key"
      SecurityGroups: ["isce-sg",]
      BlockDeviceMappings:
        -
          DeviceName: /dev/sda1
          Ebs:
            VolumeType: gp2
            VolumeSize: 8
            DeleteOnTermination: true
        -
          DeviceName: /dev/xvdf
          Ebs:
            VolumeType: gp2
            VolumeSize: 100
            DeleteOnTermination: true
      UserData:
        'Fn::Base64': !Sub |
          #!/bin/bash
          # add -xe to above line for debugging output to /var/log/cloud-init-output.log
          # create mount point directory NOTE all commands run as root
          #mkdir /mnt/data
          # create ext4 filesystem on new volume
          mkfs -t ext4 /dev/xvdf
          # add an entry to fstab to mount volume during boot
          echo "/dev/xvdf       /mnt/data   ext4    defaults,nofail 0       2" >> /etc/fstab
          # mount the volume on current boot
          mount -a
          chown -R ubuntu /mnt/data
          sudo -i -u ubuntu bash <<"EOF" 
          export PATH="/home/ubuntu/miniconda3/envs/isce-2.1.0/bin:/home/ubuntu/.local/bin:$PATH"
          export GDAL_DATA=/home/ubuntu/miniconda3/envs/isce-2.1.0/share/gdal
          source /home/ubuntu/ISCECONFIG
          # Make directories for processing - already in AMI
          cd /mnt/data
          mkdir dems poeorb auxcal
          # Get the latest python scripts from github & add to path
          git clone https://github.com/scottyhq/dinoSAR.git
          export PATH=/mnt/data/dinoSAR/bin:$PATH
          #echo $PATH
          # Download inventory file
          get_inventory_asf.py -r {roi}
          # Prepare interferogram directory
          prep_topsApp.py -i query.geojson -p {path} -m {main} -s {subordinate} -n {swaths} -r {roi} -g {gbox}
          # Run code
          cd int-{main}-{subordinate}
          topsApp.py 2>&1 | tee topsApp.log
          # Create S3 bucket and save results
          aws s3 mb s3://int-{main}-{subordinate}
          cp *xml *log merged
          aws s3 sync merged/ s3://int-{main}-{subordinate}/ 
          # Close instance
          #echo "Finished interferogram... shutting down"
          #shutdown #doesn't close entire stack, just EC2
          aws sns publish --topic-arn "arn:aws:sns:us-west-2:295426338758:email-me" --message file://topsApp.log --subject "int-{main}-{subordinate} Finished"
          aws cloudformation delete-stack --stack-name proc-{main}-{subordinate}
          EOF
'''.format(**vars(inps)))

        return filename


def launch_stack(template):
    '''
    launch AWS CloudFormationStack 
    '''
    name = template[:-4]
    cmd = 'aws cloudformation create-stack --stack-name {0} --template-body file://{1}'.format(name,template)
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
