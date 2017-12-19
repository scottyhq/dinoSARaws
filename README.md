# dinoSARaws
Interferometric Synthetic Aperture Radar (InSAR) processing with Amazon Web Services (AWS)


### What does dinoSARaws do
dinoSARaws is software that enables on-demand processing of single interferograms and sets of interferograms
 for a given area of interest in the cloud. The software includes a collection of Python scripts and [Amazon Web Services](https://aws.amazon.com) recipes. Currently, dinoSARaws works with [Sentinel-1](http://www.esa.int/Our_Activities/Observing_the_Earth/Copernicus/Sentinel-1) data, which is provided by the European Space Agency (ESA)


### Rationale
Radar remote sensing is at a pivotal moment in which cloud computing is becoming a necessary and advantageous replacement for traditional desktop scientific computing. Starting with the Sentinel-1 constellation of satellites launched by ESA in 2014 and 2016, practitioners of radar interferometry for the first time have open access to an ever-expanding global dataset.

The Sentinel-1 archive, hosted at the [ASF DAAC](https://www.asf.alaska.edu), now contains on the order of 100 images for any given location on the globe and this archive is growing at 1 Petabyte per year. In fact, NASA has [estimated that by 2025](https://earthdata.nasa.gov/about/eosdis-cloud-evolution), it will be storing upwards of 250 Petabytes (PB) of its data using commercial cloud services (e.g. Amazon Web Services).

The predicted tenfold increase in archive size is due in large part to the upcoming joint NASA/Indian Space Research Organisation (ISRO) Synthetic Aperture Radar [NISAR](https://nisar.jpl.nasa.gov) mission, which is currently scheduled to launch in 2021. NISAR data products will produce as much as 85 TB of imagery per day (45PB/year). The availability of these data in cloud environments, co-located with a wide range of cloud computing resources, could revolutionize how scientists use these datasets and provide opportunities for important scientific advancements.

dinoSARaws is an attempt to lay important groundwork for the transition to cloud computing. It is designed to be a template for other researchers to migrate their own processing and custom analysis workflows. With this in mind, it is based on purely open tools.


### How to run dinoSARaws?
dinoSARaws assumes that you have familiarity with a linux terminal, an account with AWS, and a user agreement permitting use of [ISCE Software](https://winsar.unavco.org/isce.html). There is more detailed documentation in the [docs](./docs) folder in this repository to set everything up. What follows is a quickstart tutorial for running on Ubuntu Linux.

Install Continuum Analytics Python distribution
```
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

Download dinoSARaws code (this repository)
```
git clone https://github.com/scottyhq/dinoSARaws.git
cd dinoSARaws
conda env create -f dinoSARaws.yml
source activate dinoSARaws
export PATH = `pwd`/bin:$PATH
```

Run dinoSARaws - this example processes a single interferogram covering Three Sisters Volcano in Oregon, USA
```
proc_ifg_cfn.py -i c5.4xlarge -p 115 -m 20170927 -s 20150914 -n 2 -r 44.0 44.5 -122.0 -121.5 -g 44.0 44.5 -122.0 -121.5
```


### Other SAR Cloud Computing efforts
This is a non-exhaustive list of other efforts that are leading the way:
* [hyp3](http://hyp3.asf.alaska.edu) - on demand SAR processing prototype developed at ASF for user-specified regions of interest
* [GMTSAR on AWS](https://www.asf.alaska.edu/asf-tutorials/data-recipes/gmt5sar/gmt5sar-cloud/gmt5sar-os-x/) - A nice tutorial on processing a single Sentinel-1 interferogram on AWS with [GMTSAR](http://topex.ucsd.edu/gmtsar) software.
* [GRFN](https://www.asf.alaska.edu/news-notes/2017-summer/getting-ready-for-nisar-grfn/) - prototype SAR processing on AWS using Sentinel-1 as a proxy for NISAR. Interferograms are currently generated automatically for [select locations](https://search.earthdata.nasa.gov/search?q=GRFN&ok=GRFN)
* [GeohazardsTEP](https://geohazards-tep.eo.esa.int/#!) - Cloud computing initiative from the [Committee on Earth Observation Satellites (CEOS)](http://ceos.org)
* [LicSAR](http://comet.nerc.ac.uk/COMET-LiCS-portal/) - Automated global Sentinel-1 processing with proprietary GAMMA software at COMET/University of Leeds - currently implemented for select orbital tracks and regions.
