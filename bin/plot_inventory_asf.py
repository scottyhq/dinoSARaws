#!/usr/bin/env python3
'''
Plot inventory polygon extents on a map & separate figure with timeline

Author: Scott Henderson
Date: 10/2017
ISCE: 2.1.0
'''
import argparse
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from  matplotlib.dates import YearLocator, MonthLocator, DateFormatter

from pandas.plotting import table
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.io.img_tiles import GoogleTiles

from owslib.wmts import WebMapTileService


def cmdLineParse():
    '''
    Command line parser.
    '''
    parser = argparse.ArgumentParser(description='plot_inventory_asf.py')
    parser.add_argument('-i', type=str, dest='input', required=True,
                help='Vector inventory (query.geojson)')
    parser.add_argument('-p', type=str, dest='polygon', required=False,
            help='Polygon defining region of interest')


    return parser.parse_args()


def load_inventory(vectorFile):
    '''
    load merged inventory. easy!
    '''
    gf = gpd.read_file(vectorFile)
    gf['timeStamp'] = gpd.pd.to_datetime(gf.sceneDate, format='%Y-%m-%d %H:%M:%S')
    gf['sceneDateString'] = gf.timeStamp.apply(lambda x: x.strftime('%Y-%m-%d'))
    gf['dateStamp'] = gpd.pd.to_datetime(gf.sceneDateString)
    gf['utc'] = gf.timeStamp.apply(lambda x: x.strftime('%H:%M:%S'))
    gf['relativeOrbit'] = gf.relativeOrbit.astype('int')
    gf.sort_values('relativeOrbit', inplace=True)
    gf['orbitCode'] = gf.relativeOrbit.astype('category').cat.codes
    return gf


def ogr2snwe(vectorFile):
    gf = gpd.read_file(vectorFile)
    gf.to_crs(epsg=4326, inplace=True)
    poly = gf.geometry.convex_hull
    W,S,E,N = poly.bounds.values[0]
    return [S,N,W,E]


def plot_map(gf, snwe, vectorFile=None, zoom=6):
    '''
    Use Stamen Terrain background
    '''
    pad = 1 #degrees
    S,N,W,E = snwe
    plot_CRS = ccrs.PlateCarree()
    geodetic_CRS = ccrs.Geodetic()
    x0, y0 = plot_CRS.transform_point(W-pad, S-pad, geodetic_CRS)
    x1, y1 = plot_CRS.transform_point(E+pad, N+pad, geodetic_CRS)

    fig,ax = plt.subplots(figsize=(8,8), dpi=100,
                          subplot_kw=dict(projection=plot_CRS))

    ax.set_xlim((x0, x1))
    ax.set_ylim((y0, y1))
    #ax.stock_img()
    #url = 'http://tile.stamen.com/terrain/{z}/{x}/{y}.png'
    #url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}.jpg'
    #tiler = GoogleTiles(url=url)
    #tiler = GoogleTiles() #default
    # NOTE: going higher than zoom=8 is slow...
    # How to get appropriate zoom level for static map?
    #ax.add_image(tiler, zoom)
    URL = 'http://gibs.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi'
    wmts = WebMapTileService(URL)
    #layer = 'ASTER_GDEM_Greyscale_Shaded_Relief' #ASTER_GDEM_Color_Shaded_Relief # for small regions
    layer = 'BlueMarble_ShadedRelief_Bathymetry' #BlueMarble_ShadedRelief, BlueMarble_NextGeneration
    ax.add_wmts(wmts, layer)

    states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='110m',
        facecolor='none')
    ax.add_feature(states_provinces, edgecolor='k', linestyle=':')

    #ax.add_feature(cfeature.COASTLINE)
    ax.coastlines(resolution='10m', color='black', linewidth=2)
    ax.add_feature(cfeature.BORDERS)


    # Add region of interest polygon in specified
    if vectorFile:
        tmp = gpd.read_file(vectorFile)
        ax.add_geometries(tmp.geometry.values,
                          ccrs.PlateCarree(),
                          facecolor='none',
                          edgecolor='m',
                          lw=2,
                          linestyle='dashed')

    #gf = load_inventory(args.input)
    orbits = gf.relativeOrbit.unique()
    colors = plt.cm.jet(np.linspace(0,1,orbits.size))

    #colors = plt.get_cmap('jet', orbits.size) #not iterable
    for orbit,color in zip(orbits, colors):
        df = gf.query('relativeOrbit == @orbit')
        poly = df.geometry.cascaded_union

        if df.flightDirection.iloc[0] == 'ASCENDING':
            linestyle = '--'
            #xpos, ypos = poly.bounds[0], poly.bounds[3] #upper left
            xpos,ypos = poly.centroid.x, poly.bounds[3]
        else:
            linestyle = '-'
            #xpos, ypos = poly.bounds[2], poly.bounds[1] #lower right
            xpos,ypos = poly.centroid.x, poly.bounds[1]


        ax.add_geometries([poly],
                          ccrs.PlateCarree(),
                          facecolor='none',
                          edgecolor=color,
                          lw=2, #no effect?
                          linestyle=linestyle)
        ax.text(xpos, ypos, orbit, color=color, fontsize=16, fontweight='bold', transform=geodetic_CRS)

    gl = ax.gridlines(plot_CRS, draw_labels=True,
                      linewidth=0.5, color='gray', alpha=0.5, linestyle='-')
    gl.xlabels_top = False
    gl.ylabels_left = False
    #gl.xlines = False

    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    plt.title('Sentinel-1 Orbits')
    #plt.show()
    plt.savefig('map_coverage.pdf', bbox_inches='tight')


def plot_timeline_table(gf):
    '''
    Timeline with summary table
    '''
    dfA = gf.query('platform == "Sentinel-1A"')
    dfAa = dfA.query(' flightDirection == "ASCENDING" ')
    dfAd = dfA.query(' flightDirection == "DESCENDING" ')
    dfB = gf.query('platform == "Sentinel-1B"')
    dfBa = dfB.query(' flightDirection == "ASCENDING" ')
    dfBd = dfB.query(' flightDirection == "DESCENDING" ')

    # summary table
    dfS = pd.DataFrame(index=gf.relativeOrbit.unique())
    dfS['Start'] = gf.groupby('relativeOrbit').sceneDateString.min()
    dfS['Stop'] =  gf.groupby('relativeOrbit').sceneDateString.max()
    dfS['Dates'] = gf.groupby('relativeOrbit').sceneDateString.nunique()
    dfS['Frames'] = gf.groupby('relativeOrbit').sceneDateString.count()
    dfS['Direction'] = gf.groupby('relativeOrbit').flightDirection.first()
    dfS['UTC'] = gf.groupby('relativeOrbit').utc.first()
    dfS.sort_index(inplace=True, ascending=False)
    dfS.index.name = 'Orbit'

    # Same colors as map
    orbits = gf.relativeOrbit.unique()
    colors = plt.cm.jet(np.linspace(0,1, orbits.size))

    fig,ax = plt.subplots(figsize=(11,8.5))
    #plt.scatter(dfA.timeStamp.values, dfA.orbitCode.values, c=dfA.orbitCode.values, cmap='jet', s=60, label='S1A')
    #plt.scatter(dfB.timeStamp.values, dfB.orbitCode.values, c=dfB.orbitCode.values, cmap='jet', s=60, marker='d',label='S1B')
    plt.scatter(dfAa.timeStamp.values, dfAa.orbitCode.values, c=colors[dfAa.orbitCode.values], cmap='jet', s=60, facecolor='none', label='S1A')
    plt.scatter(dfBa.timeStamp.values, dfBa.orbitCode.values, c=colors[dfBa.orbitCode.values], cmap='jet', s=60, facecolor='none', marker='d',label='S1B')
    plt.scatter(dfAd.timeStamp.values, dfAd.orbitCode.values, c=colors[dfAd.orbitCode.values], cmap='jet', s=60, label='S1A')
    plt.scatter(dfBd.timeStamp.values, dfBd.orbitCode.values, c=colors[dfBd.orbitCode.values], cmap='jet', s=60, marker='d',label='S1B')

    plt.yticks(gf.orbitCode.unique(), gf.relativeOrbit.unique())
    #plt.axvline('2016-04-22', color='gray', linestyle='dashed', label='Sentinel-1B launch')

    # Add to plot! as a custom legend
    table(ax, dfS, loc='top', zorder=10, fontsize=12,
          cellLoc = 'center', rowLoc = 'center',
          bbox=[0.1, 0.7, 0.6, 0.3] )#[left, bottom, width, height])

    ax.xaxis.set_minor_locator(MonthLocator())
    ax.xaxis.set_major_locator(YearLocator())
    plt.legend(loc='upper right')
    plt.ylim(-1,orbits.size+3)
    plt.ylabel('Orbit Number')
    fig.autofmt_xdate()
    plt.title('Sentinel-1 timeline')
    plt.savefig('timeline_with_table.pdf', bbox_inches='tight')

def plot_timeline(gf):
    '''
    Timeline with summary table
    '''
    dfA = gf.query('platform == "Sentinel-1A"')
    dfAa = dfA.query(' flightDirection == "ASCENDING" ')
    dfAd = dfA.query(' flightDirection == "DESCENDING" ')
    dfB = gf.query('platform == "Sentinel-1B"')
    dfBa = dfB.query(' flightDirection == "ASCENDING" ')
    dfBd = dfB.query(' flightDirection == "DESCENDING" ')


    # Same colors as map
    orbits = gf.relativeOrbit.unique()
    colors = plt.cm.jet(np.linspace(0,1, orbits.size))

    fig,ax = plt.subplots(figsize=(11,8.5))
    plt.scatter(dfAa.timeStamp.values, dfAa.orbitCode.values, edgecolors=colors[dfAa.orbitCode.values], facecolors='None', cmap='jet', s=60, label='Asc S1A')
    plt.scatter(dfBa.timeStamp.values, dfBa.orbitCode.values, edgecolors=colors[dfBa.orbitCode.values], facecolors='None', cmap='jet', s=60, marker='d',label='Asc S1B')
    plt.scatter(dfAd.timeStamp.values, dfAd.orbitCode.values, c=colors[dfAd.orbitCode.values], cmap='jet', s=60, label='Dsc S1A')
    plt.scatter(dfBd.timeStamp.values, dfBd.orbitCode.values, c=colors[dfBd.orbitCode.values], cmap='jet', s=60, marker='d',label='Dsc S1B')

    plt.yticks(gf.orbitCode.unique(), gf.relativeOrbit.unique())

    ax.xaxis.set_minor_locator(MonthLocator())
    ax.xaxis.set_major_locator(YearLocator())
    plt.legend(loc='lower right')
    plt.ylim(-1,orbits.size)
    plt.ylabel('Orbit Number')
    fig.autofmt_xdate()
    plt.title('Sentinel-1 timeline')
    plt.savefig('timeline.pdf', bbox_inches='tight')


if __name__ == '__main__':
    args = cmdLineParse()
    gf = load_inventory(args.input)
    w,s,e,n = gf.geometry.cascaded_union.bounds
    snwe = [s,n,w,e]
    plot_map(gf, snwe, args.polygon)
    plot_timeline(gf)
