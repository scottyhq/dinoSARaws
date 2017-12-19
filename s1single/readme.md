# Process single interferogram on AWS

## Query Sentinel1 archive via ASF

```
get_inventory_asf.py -r 44.0 44.5 -122.0 -121.5 -f
```

This will download a Geojson file (query.geojson) that describes each frame of Sentinel-1 data overlapping with a region of interest. Note that Sentinel-1 frames do not always cover the same ground footprint and can be shifted in the azimuth (roughly North-South) along a given orbital track.

Options:
* `-i` allows to input a Polygon vector file instead of `-r` for a SNWE box for the region of interest.
* `-b` adds a buffer (in degrees) around the region of interest.
* `-f` creates subfolders with geojson footprints for every S1 frame. This is convenient for checking frame overlap since you can view the frames on a map [On GitHub](https://github.com/scottyhq/pnwinsar/blob/master/oregon/frames/115/2014-11-06.geojson).

## Process a selected pair on AWS

```
proc_ifg_cfn.py -i c5.4xlarge -p 115 -m 20170927 -s 20150908 -n 2 -r 44.0 44.5 -122.0 -121.5 -g 44.0 44.5 -122.0 -121.5
```
* `-i` specifies the EC2 instance type
* `-p` specifies orbital path number 115
* `-m` specifies primary frame acquisition date
* `-s` specifies secondary frame acquisition date
* `-n` specifies subswath to process (to process all three input -n 1 2 3)
* `-r` specifies the region of interest for processing
* `-g` specifices the geocoding bounding box for ISCE outputs

This command launches computation resources on Amazon Web Services via the [AWS CloudFormation](https://aws.amazon.com/cloudformation). Essentially, the script writes a YML file (proc-20170927-20150908.yml) that specifies which computational resources to launch. In particular, a `c5.4xlarge` [EC2 Instance](https://aws.amazon.com/ec2/instance-types), with a custom Amazon Machine Image (Ubuntu 16.04 with ISCE software pre-installed). The file also specifies security settings (RSA key) and additional attached storage for running ISCE (a 100Gb [EBS drive](https://aws.amazon.com/ebs/)). Finally, a 'UserData' bash script is included at the end of the file, which runs ISCE and shuts everything down when finished. Below is a copy of the bash script:

```
#!/bin/bash
# create ext4 filesystem on attached EBS volume
mkfs -t ext4 /dev/xvdf

# add an entry to fstab to mount volume during boot
echo "/dev/xvdf       /mnt/data   ext4    defaults,nofail 0       2" >> /etc/fstab

# mount the volume on current boot
mount -a
chown -R ubuntu /mnt/data

# run the following commands as 'ubuntu' instead of root user
sudo -i -u ubuntu bash <<"EOF"
export PATH="/home/ubuntu/miniconda3/envs/isce-2.1.0/bin:/home/ubuntu/.local/bin:$PATH"
export GDAL_DATA=/home/ubuntu/miniconda3/envs/isce-2.1.0/share/gdal
source /home/ubuntu/ISCECONFIG

# Make directories for processing
cd /mnt/data
mkdir dems poeorb auxcal

# Get the latest python scripts from github & add to path
git clone https://github.com/scottyhq/dinoSARaws.git
export PATH=/mnt/data/dinoSARaws/bin:$PATH

# Download inventory file
get_inventory_asf.py -r 44.0 44.5 -122.0 -121.5

# Prepare interferogram directory
prep_topsApp.py -i query.geojson -p 115 -m 20170927 -s 20160908 -n 2 -r 44.0 44.5 -122.0 -121.5 -g 44.0 44.5 -122.0 -121.5

# Run code
cd int-20170927-20160908
topsApp.py 2>&1 | tee topsApp.log

# Create S3 bucket and save results
aws s3 mb s3://int-20170927-20160908
cp *xml *log merged
aws s3 sync merged/ s3://int-20170927-20160908/

#Close down everything
aws cloudformation delete-stack --stack-name proc-20170927-20160908
```
