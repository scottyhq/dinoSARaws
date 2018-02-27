#!/usr/bin/env python
'''
Convert geocoded ISCE output to Cloud Optimized Geotiff RGB and overviews,
making external calls to GDAL. Borrows heavily from isce2geotiff.py in ISCE
release 2.1.0. But, run after isce2cog.tif b/c operates on single band geotiffs.

Usage: isce2overviews.py path-to-merged-folder/

NOTE: currently does not inspect data for colorbar limits,,, just uses
fixed ranges that work most of the time

Scott Henderson
February 2018
'''
import os
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import numpy as np


def write_cmap(outname, vals, scalarMap):
    with open(outname, 'w') as fid:
        for val in vals:
            cval = scalarMap.to_rgba(val)
            fid.write('{0} {1} {2} {3} \n'.format(val, #value
                                                  int(cval[0]*255), #R
                                                  int(cval[1]*255), #G
                                                  int(cval[2]*255))) #B
        fid.write('nv 0 0 0 0 \n') #nodata alpha

def make_amplitude_cmap(mapname='gray', vmin=1, vmax=1e5, ncolors=64):
    cmap = plt.get_cmap(mapname)
    #vmax = get_max()
    # NOTE for strong contrast amp return:
    #cNorm = colors.Normalize(vmin=1e3, vmax=1e4)
    cNorm = colors.LogNorm(vmin=vmin, vmax=vmax)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)
    vals = np.linspace(vmin, vmax, ncolors, endpoint=True)
    outname = 'amplitude-cog.cpt'
    write_cmap(outname, vals, scalarMap)

    return outname

def make_wrapped_phase_cmap(mapname='plasma', vmin=-50, vmax=50, ncolors=64, wrapRate=6.28):
    ''' each color cycle represents wavelength/2 LOS change '''
    cmap = plt.get_cmap(mapname)
    cNorm = colors.Normalize(vmin=0, vmax=1) #re-wrapping normalization
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)
    vals = np.linspace(vmin, vmax, ncolors, endpoint=True)
    vals_wrapped = np.remainder(vals, wrapRate) / wrapRate
    # NOTE: if already converted to cm:
    #vals_wrapped = np.remainder(vals - vals.min(), wavelength/2.0) / (wavelength/2.0)
    outname = 'unwrapped-phase-cog.cpt'
    with open(outname, 'w') as fid:
        for val, wval in zip(vals, vals_wrapped):
            cval = scalarMap.to_rgba(wval)
            fid.write('{0} {1} {2} {3} \n'.format(val, #value
                                                  int(cval[0]*255), #R
                                                  int(cval[1]*255), #G
                                                  int(cval[2]*255))) #B
        fid.write('nv 0 0 0 0 \n') #nodata alpha

    return outname


def make_coherence_cmap(mapname='inferno', vmin=1e-5, vmax=1, ncolors=64):
    cmap = plt.get_cmap(mapname)
    cNorm = colors.Normalize(vmin=vmin, vmax=vmax)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)
    vals = np.linspace(vmin, vmax, ncolors, endpoint=True)
    outname = 'coherence-cog.cpt'
    write_cmap(outname, vals, scalarMap)

    return outname


def make_rgb(infile, cptfile):
    outfile = infile[:-4] + '-rgb.tif'
    cmd = f'gdaldem color-relief -alpha {infile} {cptfile} {outfile}'
    print(cmd)
    os.system(cmd)
    return outfile


def make_thumbnails(infile, small=5, large=10):
    '''
    Make a large and small png overview
    '''
    outfile = infile[:-4] + '-thumb-large.png'
    cmd = f'gdal_translate -of PNG -r cubic -outsize {large}% 0 {infile} {outfile}'
    print(cmd)
    os.system(cmd)
    outfile = infile[:-4] + '-thumb-small.png'
    cmd = f'gdal_translate -of PNG -r cubic -outsize {small}% 0 {infile} {outfile}'
    print(cmd)
    os.system(cmd)


def make_overviews(infile):
    ''' Note: automatically warps to EPSG:3587
    note: could change title and add copyright!
    '''
    cmd = f'gdal2tiles.py -w leaflet -z 6-12 {infile}'
    print(cmd)
    os.system(cmd)

def clean_up(infile):
    ''' Note: remove large full resolution RGBA files'''
    # NOTE: should probably upload .cpt files so that they are easy to re-generate
    cmd = 'rm *rgb.tif tmp*'
    print(cmd)
    os.system(cmd)

if __name__ == '__main__':
    #toConvert = {'amplitude-cog.tif':(1,10e3), #amp return
    #             'unwrapped-phase.tif':(-50,50), #radians (*(5.546576/12.5663706 for meters)
    #              'coherence-cog.tif':(0,1),
    #              'elevation-cog.tif':(0,1000)}
    infile =  'coherence-cog.tif'
    cptFile = make_coherence_cmap()
    rgbFile = make_rgb(infile, cptFile)
    make_thumbnails(rgbFile)
    make_overviews(rgbFile)

    infile =  'amplitude-cog.tif'
    cptFile = make_amplitude_cmap()
    rgbFile = make_rgb(infile, cptFile)
    make_thumbnails(rgbFile)
    make_overviews(rgbFile)

    infile = 'unwrapped-phase-cog.tif'
    cptFile = make_wrapped_phase_cmap()
    rgbFile = make_rgb(infile, cptFile)
    make_thumbnails(rgbFile)
    make_overviews(rgbFile)

    print('Done!')
    print('Run these to move files to S3:')
    #Copy pngs NOTE: this recursively goes into overview folders!
    print('aws s3 sync . s3://int-[date1]-[date2] --exclude "*" --include "*png"')
    print('aws s3 sync . s3://int-[date1]-[date2] --exclude "*" --include "*cpt"')
    print('aws s3 sync . s3://int-[date1]-[date2] --exclude "*" --include "*html"')
