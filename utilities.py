import numpy as np

def utcOffset(timezone):

    timeZones = {'UTC': 0, 'AZOST': -1, 'MAST': -2, 'GST': -3,
                 'AST': -4, 'EST': -5, 'CST': -6, 'MST': -7, 
                 'PST':-8, 'AKST':-9, 'HST':-10, 'SST': -11, 'DST': -12}

    daylightOffset = 0
    if timezone.endswith('DT'):
        daylightOffset = 1
        timezone = timezone.replace('D','S')
    offset = timeZones.get(timezone) + daylightOffset
    return offset

def calculateDistance(start_lat,end_lat,dlat, dlon):

    a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(start_lat)*np.cos(end_lat)*np.sin(dlon/2)*np.sin(dlon/2)
    c = 2*np.arctan2(np.sqrt(a), np.sqrt(1-a))
    d = 6371000*c
    return d

def calculateBearing(start_lat,end_lat,dlat, dlon):

    y = np.sin(dlon) * np.cos(end_lat)
    x = np.cos(start_lat)*np.sin(end_lat) - np.sin(start_lat)*np.cos(end_lat)*np.cos(dlon)

    bearing = (np.degrees(np.arctan2(y,x))+360) % 360
    bearing *= np.pi/180.
    return bearing

def interpolatePoint(start_lon,start_lat,dist,bearing,time,timedelta):
    distance = dist*time/timedelta
    r = 6371000
    interpolated_lat = np.arcsin(np.sin(start_lat)*np.cos(distance/r) + 
                       np.cos(start_lat)*np.sin(distance/r)*np.cos(bearing))
    interpolated_lon = (start_lon + np.arctan2(np.sin(bearing)*np.sin(distance/r)*np.cos(start_lat), np.cos(distance/r) - np.sin(start_lat)*np.sin(interpolated_lat)))
    return interpolated_lon*180/np.pi, interpolated_lat*180/np.pi

def get_cmap(infile):
    if 'sat_BW' in infile:
        max_val = 300
        min_val = 182
        position = [0,1]
    if 'sat_IR' in infile:
        max_val = 300
        min_val = 170
        position = [0,(200.-min_val)/(max_val-min_val),
             (208.-min_val)/(max_val-min_val),
             (218.-min_val)/(max_val-min_val),
             (228.-min_val)/(max_val-min_val),
             (245.-min_val)/(max_val-min_val),
             (253.-min_val)/(max_val-min_val),
             (258.-min_val)/(max_val-min_val),1]
    if 'sat_SPoRT' in infile:
        max_val = 330
        min_val = 181
        position = [0,(193.-min_val)/(max_val-min_val),
             (193.-min_val)/(max_val-min_val),
             (203.-min_val)/(max_val-min_val),
             (213.-min_val)/(max_val-min_val),
             (223.-min_val)/(max_val-min_val),
             (228.-min_val)/(max_val-min_val),
             (240.-min_val)/(max_val-min_val),
             (243.-min_val)/(max_val-min_val),
             (245.-min_val)/(max_val-min_val),
             (254.-min_val)/(max_val-min_val),
             (254.-min_val)/(max_val-min_val),1]
    elif 'sat_BD' in infile:
        max_val = 303
        min_val = 183
        position = [0,(188.-min_val)/(max_val-min_val),
             (188.-min_val)/(max_val-min_val),
             (194.-min_val)/(max_val-min_val),
             (194.-min_val)/(max_val-min_val),
             (199.-min_val)/(max_val-min_val),
             (199.-min_val)/(max_val-min_val),
             (205.-min_val)/(max_val-min_val),
             (205.-min_val)/(max_val-min_val),
             (211.-min_val)/(max_val-min_val),
             (211.-min_val)/(max_val-min_val),
             (221.-min_val)/(max_val-min_val),
             (221.-min_val)/(max_val-min_val),
             (233.-min_val)/(max_val-min_val),
             (233.-min_val)/(max_val-min_val),
             (254.-min_val)/(max_val-min_val),
             (254.-min_val)/(max_val-min_val),
             (283.-min_val)/(max_val-min_val),
             (283.-min_val)/(max_val-min_val),1]
        print(len(position))
    new_cmap = make_cmap(infile, position=position)
    return min_val, max_val, new_cmap

def truncate_cmap (cmap,n_min=0,n_max=256):
   import matplotlib.pyplot as plt
   color_index = np.arange(n_min,n_max).astype(int)
   colors = cmap(color_index)
   name = "truncated_{}".format(cmap.name)
   return plt.matplotlib.colors.ListedColormap(colors,name=name)

def make_cmap(colortable, position=None, bit=False):
   import sys
   import matplotlib as mpl
   import os
   #Create full name
   file_path = colortable+'.txt'
   #Read file
   colors = np.loadtxt(file_path,skiprows=1)

   bit_rgb = np.linspace(0,1,256)
   if position == None:
       position = np.linspace(0,1,len(colors))
   else:
       if len(position) != len(colors):
           sys.exit("position length must be the same as colors")
       elif position[0] != 0 or position[-1] != 1:
           sys.exit("position must start with 0 and end with 1")
   if bit:
       for i in range(len(colors)):
           colors[i] = (bit_rgb[colors[i][0]],
                        bit_rgb[colors[i][1]],
                        bit_rgb[colors[i][2]])
   cdict = {'red':[], 'green':[], 'blue':[]}
   for pos, color in zip(position, colors):
       cdict['red'].append((pos, color[0], color[0]))
       cdict['green'].append((pos, color[1], color[1]))
       cdict['blue'].append((pos, color[2], color[2]))

   cmap = mpl.colors.LinearSegmentedColormap(os.path.basename(colortable),cdict,256)
   return cmap
