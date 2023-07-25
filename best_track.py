import urllib.request
from zipfile import ZipFile
import xmltodict
import datetime

def track(atcfid):

    path = 'https://www.nhc.noaa.gov/gis/best_track/' + atcfid + '_best_track.kmz'

    fname, headers = urllib.request.urlretrieve(path)
    kmz = ZipFile(fname,'r')
    kml_fname = atcfid + '.kml'
    kml = kmz.open(kml_fname,'r')

    track = xmltodict.parse(kml.read())

    placeMarks = track.get('kml').get('Document').get('Folder')[0].get('Placemark')

    lon = [] ; lat = [] ; intensity = [] ; date = []
    for index, placeMark in enumerate(placeMarks):
        tmp = datetime.datetime.strptime(placeMark.get('name'),"%H%M UTC %b %d")
        date.append(tmp.replace(year = int(atcfid[-4:])))
        coordinates = placeMark.get('Point').get('coordinates').split(',')
        lon.append(float(coordinates[0]))
        lat.append(float(coordinates[1]))
        intensity.append(placeMark.get('intensity'))

    return date, lat, lon, intensity

