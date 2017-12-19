# Process an entire set of interferograms on AWS

This folder contains code to processes several hundred interferograms efficiently in the cloud.

## Why run this?

Individual interferograms theoretically measure relative ground displacement between two dates. However, single images are often dominated by atmospheric noise (phase delays caused by water vapor). Stratified changes in water vapor can sometimes successfully eliminated using regional weather models or empirical relations of phase difference to elevation. Turbulent atmospheric noise can be estimated with stacks of many interferograms and time series since these variations are expected to be uncorrelated in time. In short, processing a set of interferograms allows for more sophisticated analysis to isolate true ground deformation.

## Common master processes

Intended to pair most recent acquisition with several preceding acquisitions

```
proc_batch_master.py -p 115 -m 20170927 -s 3 -n 2 -r 44.0 44.5 -122.0 -121.5 -g 44.0 44.5 -122.0 -121.5
```

* `-s 3` specifies processing of 20170927 with three preceding dates:

```
int-20170927-20170915
int-20170927-20170903
int-20170927-20170812
```

## Entire archive processing

**Be warned**, depending on the size of your region of interest this can be quite expensive. Essentially, for a set of frames covering your area of interest, each sequential pairing of dates is sent to a different virtual machine to be processed in parallel. This is accomplished via [AWS Batch](https://aws.amazon.com/batch/).

```
proc_batch_sequential.py -p 115 -n 2 -r 44.0 44.5 -122.0 -121.5 -g 44.0 44.5 -122.0 -121.5
```
