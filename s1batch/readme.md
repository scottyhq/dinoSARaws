# Process an entire set of interferograms on AWS

This folder contains code to processes several hundred interferograms efficiently in the cloud. **Be warned**, depending on the size of your region of interest this can be quite expensive. Essentially, for an set of frames covering your area of interest, each sequential pairing of dates is send to a different virtual machine to be processed in parallel. This is accomplished via [AWS Batch](https://aws.amazon.com/batch/).

## Why run this?

Individual 
