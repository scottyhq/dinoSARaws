#!/usr/bin/env python
'''
Convert geocoded ISCE output to Cloud Optimized Geotiffs

Usage: isce2cog.tif path-to-merged-folder/

filt_topophase.unw.geo --> amplitude-cog.tif, unwrapped-phase-cog.tif
phsig.cor.geo.vrt --> coherence-cog.tif
los.rdr.geo.vrt --> incidence-cog.tif, heading-cog.tif
dem.crop.vrt --> elevation-cog.tif

http://www.cogeo.org

Scott Henderson
February 2018
'''

import os

def extract_band(infile, band):
    cmd = f'gdal_translate -of VRT -b {band} -a_nodata 0.0 {infile} tmp.vrt'
    print(cmd)
    os.system(cmd)

def make_overviews():
    cmd = 'gdaladdo tmp.vrt 2 4 8 16 32'
    print(cmd)
    os.system(cmd)

def make_cog(outfile):
    cmd = f'gdal_translate tmp.vrt {outfile} -co COMPRESS=DEFLATE \
-co TILED=YES -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 \
-co COPY_SRC_OVERVIEWS=YES  --config GDAL_TIFF_OVR_BLOCKSIZE 512'
    print(cmd)
    os.system(cmd)

def clean_up():
    os.system('rm tmp*')


if __name__ == '__main__':
    conversions = {'amplitude-cog.tif' : ('filt_topophase.unw.geo.vrt',1),
                   'unwrapped-phase-cog.tif' : ('filt_topophase.unw.geo.vrt',2),
                   'coherence-cog.tif' : ('phsig.cor.geo.vrt',1),
                   'incidence-cog.tif' : ('los.rdr.geo.vrt',1),
                   'heading-cog.tif' : ('los.rdr.geo.vrt',2),
                   'elevation-cog.tif' : ('dem.crop.vrt',1)}

    for outfile,(infile,band) in conversions.items():
        print(infile, band, outfile)
        extract_band(infile, band)
        make_overviews()
        make_cog(outfile)
        clean_up()

    print('Done!')
