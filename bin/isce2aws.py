#!/usr/bin/env python
'''
Convert ISCE to cloud-friendly outputs and push to s3

Usage: isce2aws.py int-20170828-20170816
'''
import isce2cog
import isce2overviews
import os
import sys

def cleanUp():
    '''
    remove tmp and unneeded files
    '''
    cmd = 'rm tmp* *rgb.tif'

def writeIndex(intname):
    '''
    super simple HTML index
    '''
    with open('indexTemplate.html') as template:
        text = template.read()
        formattedText = .format(intname=intname)
        with open('index.html', 'w') as index:
            index.write(formattedText)

# Get interferogram name from command line argument
intname = sys.argv[1]

conversions = {'amplitude-cog.tif' : ('filt_topophase.unw.geo.vrt',1),
               'unwrapped-phase-cog.tif' : ('filt_topophase.unw.geo.vrt',2),
               #'coherence-cog.tif' : ('phsig.cor.geo.vrt',1),
               'coherence-cog.tif' : ('topophase.cor.geo.vrt',1),
               'incidence-cog.tif' : ('los.rdr.geo.vrt',1),
               'heading-cog.tif' : ('los.rdr.geo.vrt',2),
               'elevation-cog.tif' : ('dem.crop.vrt',1)}

# Create Cloud-optimized geotiffs of select output files
for outfile,(infile,band) in conversions.items():
    print(infile, band, outfile)
    isce2cog.extract_band(infile, band)
    isce2cog.make_overviews()
    isce2cog.make_cog(outfile)

# Create RGB thumbnails and tiles
infile =  'coherence-cog.tif'
cptFile = isce2overviews.make_coherence_cmap()
rgbFile = isce2overviews.make_rgb(infile, cptFile)
isce2overviews.make_thumbnails(rgbFile)
isce2overviews.make_overviews(rgbFile)

infile =  'amplitude-cog.tif'
cptFile = isce2overviews.make_amplitude_cmap()
rgbFile = isce2overviews.make_rgb(infile, cptFile)
isce2overviews.make_thumbnails(rgbFile)
isce2overviews.make_overviews(rgbFile)

infile = 'unwrapped-phase-cog.tif'
cptFile = isce2overviews.make_wrapped_phase_cmap()
rgbFile = isce2overviews.make_rgb(infile, cptFile)
isce2overviews.make_thumbnails(rgbFile)
isce2overviews.make_overviews(rgbFile)

# Clean up temporary files, etc
cleanUp()

# Write an html index file
writeIndex()

# Push everything to s3
os.mkdir('output')
cmd = 'mv index.html *-cog-* output'
cmd = f'aws s3 sync output s3://{intname}/output'
print(cmd)
os.system(cmd)

print('All done!')
