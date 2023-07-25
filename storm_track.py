import csv
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import glob
import os

atcfid = 'al062018'

time = []
lon = []
lat = []
intensity = []

with open(atcfid + '/locations.csv') as input_file:
    reader = csv.reader(input_file, delimiter=',')
    next(reader)
    for row in reader:
        time.append(datetime.datetime.strptime(row[0],"%Y-%m-%dT%H:%M:%S"))
        lon.append(float(row[1]))
        lat.append(float(row[2]))
        intensity.append(int(row[3]))

time = np.asarray(time) ; lon = np.asarray(lon)
lat = np.asarray(lat) ; intensity = np.asarray(intensity)

bounds = [0,34,64,83,96,113,137,165]
norm = mpl.colors.BoundaryNorm(bounds,256)
colormap = mpl.cm.jet
filenames = sorted(glob.glob(os.getcwd() + '/' + atcfid + '/predictions/*.png'))
for i in range(len(filenames)):
    filename = filenames[i].split('/')[-1].split('.png')[0]
    print(filename)
    #extent = [np.amin(lon[:i])-5,np.amax(lon[:i])+5,np.amin(lat[:i])-5,np.amax(lat[:i])+5]
    #extent = [-180,90,-90,90]
    fig = plt.gcf()
    projection=ccrs.Orthographic(central_longitude=lon[i],central_latitude=lat[i])
    geo = ccrs.Geodetic()
    ax = plt.axes([0.0,0.01,0.98,0.975],projection=projection)
    #ax.set_extent(extent)
    ax.background_img(name="BM",resolution="low")
    ax.coastlines(resolution='50m',color='k')
    ax.add_feature(cartopy.feature.BORDERS,color='k')
    states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='50m',
        facecolor='none')
    ax.add_feature(states_provinces, edgecolor='k')
    #ax.plot([lon[:i]],[lat[:i]],color='white',zorder=9,linewidth=2,transform=ccrs.Geodetic())
    ax.scatter([lon[i]],[lat[i]],c=[intensity[i]],s=[intensity[i]]*3,cmap=colormap,
               norm=norm,marker="o",edgecolor='white',zorder=10,transform=geo)
    if i > 0:
        ax.scatter([lon[:i]],[lat[:i]],c=[intensity[:i]],s=12,cmap=colormap,
                   norm=norm,marker="o",zorder=9,transform=geo)
    #if (i+1) % 36 == 0 or (i+1) >= 36:
    #    print('here')
    #    ax.scatter(lon[0:i:36],lat[0:i:36],c=intensity[0:i:36],s=intensity[0:i:36],cmap=colormap,
    #               norm=norm,marker='o',edgecolor='white',zorder=10,transform=geo)
    cax = fig.add_axes([0.85,0.05,0.025,0.9])
    cbar = mpl.colorbar.ColorbarBase(cax, cmap='jet',
                                     norm=norm,
                                     orientation='vertical')
    cbar.set_label('Saffir-Simpson Hurricane Wind Scale',fontsize=30)
    cbar.set_ticks((np.array(bounds[0:-1]) + np.array(bounds[1::]))/2)
    cbar.ax.set_yticklabels(['TD','TS','Cat 1','Cat 2','Cat 3','Cat 4','Cat 5'],fontsize=24)
    fig.set_size_inches(16,9)
    fig.savefig(atcfid + '/track/' + filename,pad=0,dpi=100)
    plt.close('all')
