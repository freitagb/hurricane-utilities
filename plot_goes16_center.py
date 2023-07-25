#import libraries for radar visualization
import numpy as np
import datetime
import glob
import json
import os
import boto
import tempfile
import netCDF4
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
#from mpl_toolkits.basemap import Basemap
#suppress deprecation warnings
import warnings
warnings.simplefilter("ignore", category=DeprecationWarning)
from best_track import track
from utilities import *
import csv

class goes16:

    def __init__(self):
        with open('config.json') as json_data:
            config = json.load(json_data)
        self.path = config.get('path')
        self.savedir = config.get('savedir','./')
        self.plot = config.get('plot', False)
        self.time_index = None

    def get_files(self, product, scan, bandno, year, day, hour, minute):
        s3conn = boto.connect_s3()
        bucket = s3conn.get_bucket('noaa-goes16')
        yr = "{:4d}".format(year) ; dy = "{:03d}".format(day)
        hr = "{:02d}".format(hour) ; mn = "{:02d}".format(minute)
        path = '/'.join([product, yr, dy, hr, 'OR_' + product + '-' + scan + 'C' + "{0:02}".format(bandno)])
        ls = bucket.list(prefix=path, delimiter='/')
        return bucket, ls

    def read_nc_data(self,fname):
        print(fname.key.key)
        self.infile = tempfile.NamedTemporaryFile(delete=False)
        fname.get_contents_to_filename(self.infile.name)
        self.ncId = netCDF4.Dataset(self.infile.name, 'r')

    def create_projection(self):
        rad2deg = 180./np.pi
        x1 = self.ncId.variables['x'][:]
        y1 = self.ncId.variables['y'][:]
        goes_imager_projection = self.ncId.variables['goes_imager_projection']
        req = goes_imager_projection.semi_major_axis
        rpol = goes_imager_projection.semi_minor_axis
        H = goes_imager_projection.perspective_point_height + req
        lon0 = goes_imager_projection.longitude_of_projection_origin
        x,y = np.meshgrid(x1,y1)
        #Calculate variables
        a = (np.sin(x))**2 + (np.cos(x)**2)*((np.cos(y)**2) + (req**2/rpol**2)*(np.sin(y)**2))
        b = -2.*H*np.cos(x)*np.cos(y)
        c = H**2 - req**2
        rs = (-1.*b - np.sqrt(b**2 - 4*a*c))/(2*a)
        sx = rs*np.cos(x)*np.cos(y)
        sy = -1.*rs*np.sin(x)
        sz = rs*np.cos(x)*np.sin(y) 
             
        #Calculate lat/lon
        self.lat = np.asarray(np.arctan((req**2/rpol**2)*(sz/np.sqrt((H-sx)**2 + sy**2))) * rad2deg)
        self.lon = np.asarray(lon0 - np.arctan(sy/(H-sx)) * rad2deg)

        geospatial_lat_lon_extent = self.ncId.variables['geospatial_lat_lon_extent']
        self.lat0 = geospatial_lat_lon_extent.geospatial_lat_center
        self.lon0 = geospatial_lat_lon_extent.geospatial_lon_center

        self.ll_lon = geospatial_lat_lon_extent.geospatial_westbound_longitude
        self.ur_lon = geospatial_lat_lon_extent.geospatial_eastbound_longitude
        self.ll_lat = geospatial_lat_lon_extent.geospatial_southbound_latitude
        self.ur_lat = geospatial_lat_lon_extent.geospatial_northbound_latitude


    def get_rad(self):
        rad = self.ncId.variables['Rad'][:]
        self.pvar = rad

    def get_tb(self):
        rad = self.ncId.variables['Rad'][:]
        #Read in the constants from the netCDF file
        fk1 = self.ncId.variables['planck_fk1'][0]
        fk2 = self.ncId.variables['planck_fk2'][0]
        bc1 = self.ncId.variables['planck_bc1'][0]
        bc2 = self.ncId.variables['planck_bc2'][0]

        #Calculate brightness temperature [K]
        self.pvar = (fk2 / (np.log((fk1/rad)+1)) - bc1) / bc2

    def get_time(self):
        t = np.mean(self.ncId.variables['t'][:])
        start = datetime.datetime(2000,1,1,12,0,0)
        dt = datetime.timedelta(seconds=t)
        self.time = start + dt
        print(self.time)


    def get_bounds(self,date,lat,lon,intensity,bufferinDegrees):
        for i,dt in enumerate(date):
            if dt < self.time:
                self.time_index = i
        if self.time_index is None:
            return None
        else:
            self.advTime = date[self.time_index].strftime("%Y%m%dT%H%M%S")
            self.goesTime = self.time.strftime("%Y%m%dT%H%M%S")
            self.intensity = intensity[self.time_index]
            time = date[self.time_index]
            timeOffset = self.time - time
            timeDiff =(date[self.time_index+1] - time)
            start_lat = lat[self.time_index]*np.pi/180.
            end_lat = lat[self.time_index+1]*np.pi/180.
            dlat = (end_lat - start_lat)
            start_lon = lon[self.time_index]*np.pi/180.
            end_lon = lon[self.time_index+1]*np.pi/180.
            dlon = (end_lon - start_lon)
            dist = calculateDistance(start_lat,end_lat,dlat,dlon)
            bearing = calculateBearing(start_lat,end_lat,dlat,dlon)
            self.newCenterLon, self.newCenterLat = interpolatePoint(start_lon,start_lat,dist,bearing,timeOffset, timeDiff)
            ll_lon = self.newCenterLon - bufferinDegrees ; ur_lon = self.newCenterLon + bufferinDegrees
            ll_lat = self.newCenterLat - bufferinDegrees ; ur_lat = self.newCenterLat + bufferinDegrees
            return [ll_lon, ur_lon, ll_lat, ur_lat]
        
        
    def plot_tb(self, it, atcfid, cmap = 'jet', bbox = None):
        #set up a 1x1 figure for plotting
        self.savedir = self.savedir.format(atcfid)
        if not os.path.isdir(self.savedir):
            os.mkdir(self.savedir)
        print(self.savedir)
        imageFileName = '_'.join([atcfid,'advTime',self.advTime,'goesTime',self.goesTime,'intensity', self.intensity]) + 'kts.png'
        '''
        #Basemap implementation
        m = Basemap(projection='cyl', lat_0=self.newCenterLat, lon_0=self.newCenterLon,
                    llcrnrlon=bbox[0], llcrnrlat=bbox[2],
                    urcrnrlon=bbox[1], urcrnrlat=bbox[3])
        norm = mpl.colors.Normalize(vmin=self.min_val,vmax=self.max_val)
        m.pcolormesh(self.lon,self.lat,self.pvar,norm=norm,cmap=cmap) 
        m.imshow(self.pvar[lon_ind,lat_ind], vmin=self.min_val, vmax=self.max_val, cmap=cmap,extent=bbox)
        '''
        #'''
        #Cartopy implementation - needs work
        proj = ccrs.PlateCarree()
        ax = plt.axes([0,0,1,1], projection=proj)
        ax.set_extent(bbox,crs=proj)
        norm = mpl.colors.Normalize(vmin=self.min_val,vmax=self.max_val)
        # hack to avoid missing data in pcolormesh
        start_indx = 1000
        start_indy = 1000
        end_indx = 4500
        end_indy = 4500
        x = self.lon[start_indx:end_indx,start_indy:end_indy]
        y = self.lat[start_indx:end_indx,start_indy:end_indy]
        pvar = self.pvar[start_indx:end_indx,start_indy:end_indy]
        ax.pcolormesh(x,y,pvar,norm=norm,cmap=cmap,transform=proj)
        '''
        plt.savefig(self.savedir + '/' + imageFileName, bbox_inches='tight', pad_inches=-0.05, dpi=300)
        plt.close('all')


    def GOES16(self, atcfid, bufferinDegrees=5):
        date, lat, lon, intensity = track(atcfid)
        julian_day = np.arange(date[0].timetuple().tm_yday,date[-1].timetuple().tm_yday+1,1)
        scan_strategy = {2019: "M6"}
        with open('locations.csv','w') as output_file:
            wr = csv.writer(output_file,dialect='excel')
            wr.writerow(['Time','Longitude','Latitude','Intensity'])
            for jd in julian_day[1:]:
                for h in range(1,24):
                        bucket, ls = self.get_files(product='ABI-L1b-RadF',scan=scan_strategy.get(int(atcfid[-4:]),'M3'),bandno=13,year=int(atcfid[-4:]),day=jd,hour=h,minute=1)
                        latlon = False
                        print(len(list(ls)))
                        if len(list(ls)) > 0:
                            for i,item in enumerate([list(ls)[0]]):
                                s3key = bucket.get_key(item)
                                self.read_nc_data(s3key)
                                self.get_time()
                                bounds = self.get_bounds(date,lat,lon,intensity,bufferinDegrees)
                                #interpolatedLon.append(self.newCenterLon) ; interpolatedLat.append(self.newCenterLat)
                                if bounds is not None:
                                    wr.writerow([self.time.strftime("%Y-%m-%dT%H:%M:%S"),self.newCenterLon,self.newCenterLat,self.intensity])
                                if self.plot and bounds is not None:
                                    if not latlon:
                                        self.create_projection()
                                        latlon=True
                                    self.get_tb()
                                    self.min_val, self.max_val, new_cmap = get_cmap('goes_colortables/sat_BW')
                                    plt.register_cmap(cmap=new_cmap)
                                    self.cmap=new_cmap
                                    self.plot_tb(i, atcfid, cmap='sat_BW', bbox=bounds)
                                self.ncId.close()
                                os.remove(self.infile.name)


