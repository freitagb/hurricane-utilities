import matplotlib as mpl
import matplotlib.pyplot as plt
import glob
import numpy as np
import datetime

atcfid = 'al052019'

files = sorted(glob.glob(atcfid + '/maps/*.png'))
time = [] ; advSpeed = [] ; hieSpeed = []
indTime = None ; indIntensity = None
for file in files:
    tmp = file.split('_')
    if indTime is None:
        indTime = np.argwhere(np.asarray(tmp) == 'goesTime')[0][0]
        print(indTime)
    if indIntensity is None:
        indIntensity = np.argwhere(np.asarray(tmp) == 'intensity')[0][0]
        print(indIntensity)
    time.append(datetime.datetime.strptime(tmp[indTime+1],"%Y%m%dT%H%M%S"))
    advSpeed.append(float(tmp[indIntensity+1][:-3]))
    hieSpeed.append(float(tmp[indIntensity+2]))

#convert lists to arrays and get bounds for y-axis
advSpeed = np.asarray(advSpeed)
hieSpeed = np.asarray(hieSpeed)
maxIntensity = max(np.amax(advSpeed),np.amax(hieSpeed))
minIntensity = min(np.amin(advSpeed),np.amin(hieSpeed))
print(minIntensity, maxIntensity)

#setup the plot stuff
intensityBuffer=5
dates = np.asarray(mpl.dates.date2num(time))
hours = mpl.dates.HourLocator(interval=6)
days = mpl.dates.DayLocator()
day_fmt = mpl.dates.DateFormatter('%b-%d')
yticks = np.array([minIntensity,34,64,83,96,113,137,maxIntensity+intensityBuffer])
yticks_pos = (yticks[:-1] + yticks[1::])/2.
yticklabels = ['TD','TS', 'Cat 1', 'Cat 2', 'Cat 3', 'Cat 4', 'Cat 5']
print(yticks_pos)
advs = []

for i in range(len(dates)):
    fname = '_'.join(files[i].split('_')[2:-2]) + '_estimate_' + files[i].split('_')[-2].split('.')[0] + 'kts.png'
    print(fname)
    fig = mpl.pyplot.gcf()
    fig.patch.set_facecolor('darkgray') ; fig.patch.set_alpha(0.8)
    plt.xlim(dates[0],dates[-1])
    ax = plt.gca()
    ax.patch.set_facecolor('darkgray') ; ax.patch.set_alpha(0.2)
    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(day_fmt)
    ax.xaxis.set_minor_locator(hours)
    ax.tick_params(axis='x',labelsize=28,length=8,width=2)
    ax.tick_params(which='minor',length=4)
    ax.yaxis.set_major_formatter(mpl.ticker.NullFormatter())
    plt.yticks(ticks=yticks[1:-1])
    ax.yaxis.set_minor_locator(mpl.ticker.FixedLocator(yticks_pos))
    ax.yaxis.set_minor_formatter(mpl.ticker.FixedFormatter(yticklabels))
    ax.tick_params(which='minor', axis='y',labelsize=30,length=0,width=0)
    ax.tick_params(which ='major',axis='y',labelsize=0,length=8,width=2)
    plt.ylim(minIntensity,maxIntensity+intensityBuffer)
    #plt.ylabel('Saffir-Simpson Scale',fontsize=30)
    #plt.yticks(ticks=yticks, labels=yticklabels)
    plt.plot_date(dates[:i],advSpeed[:i],fmt='-',linewidth=4,color='b', label='Forecast Advisory')
    plt.plot_date(dates[:i],hieSpeed[:i],fmt='-',linewidth=4,color='g',label='ML Estimate')
    plt.plot_date(dates[i],advSpeed[i],fmt='o', markersize=10,color='b')
    plt.plot_date(dates[i],hieSpeed[i],fmt='o', markersize=10,color='g')

    if advSpeed[i] < 34:
        rating = 'Tropical Depression'
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],0,34, color='yellow',alpha=0.5,zorder=0)
    if advSpeed[i] >=34 and advSpeed[i] < 64:
        rating = 'Tropical Storm'
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],0,34, color='yellow',alpha=0.15,zorder=0)
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],34,64, color='yellow',alpha=0.5,zorder=0)
    if advSpeed[i] >= 64 and advSpeed[i] < 83:
        rating = 'Category 1'
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],0,64, color='yellow',alpha=0.15,zorder=0)
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],64,83, color='yellow',alpha=0.5,zorder=0)
    if advSpeed[i] >= 83 and advSpeed[i] < 96:
        rating = 'Category 2'
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],0,83, color='yellow',alpha=0.15,zorder=0)
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],83,96, color='yellow',alpha=0.5,zorder=0)
    if advSpeed[i] >= 96 and advSpeed[i] < 114:
        rating = 'Category 3'
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],0,96, color='yellow',alpha=0.15,zorder=0)
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],96,113,color='yellow',alpha=0.5,zorder=0)
    if advSpeed[i] >= 113 and advSpeed[i] < 137:
        rating = 'Category 4'
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],0,113, color='yellow',alpha=0.15,zorder=0)
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],113,137, color='yellow',alpha=0.5,zorder=0)
    if advSpeed[i] >= 137:
        rating = 'Category 5'
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],0,137, color='yellow',alpha=0.15,zorder=0)
        ax.fill_between([dates[0],dates[0],dates[-1],dates[-1]],137,maxIntensity+intensityBuffer, color='yellow',alpha=0.5,zorder=0)

    '''
    if (i+1) % 6 == 0:
        advs.append([i])
        tmp = np.asarray(advs)
    print(advSpeed[tmp[0]],dates[tmp][0])
    if len(advs) > 0:
        plt.plot_date(dates[tmp],advSpeed[tmp],fmt='-o',markersize=5,color='b')#,xdate=True,ydate=False,color='b')
        plt.plot_date(dates[tmp],hieSpeed[tmp],fmt='-o',markersize=5,color='g')#,xdate=True,ydate=False,color='g')
    '''
    fig.autofmt_xdate()
    plt.legend(loc=1,fontsize=24,facecolor='white',edgecolor='black',fancybox=True,framealpha=1)
    plt.text(dates[26],maxIntensity+intensityBuffer - 13, "Official Intensity: " + rating,fontsize=30)
    plt.text(dates[26], maxIntensity+intensityBuffer - 23, 'Max Wind Speed: ' + "{:d}".format(int(advSpeed[i])) + ' kts',fontsize=30) 
    #set up axis for wind speed
    ax2 = ax.twinx()
    ax2.set_ylim(minIntensity,maxIntensity+intensityBuffer)
    ax2.set_yticks(yticks[1:-1])
    ax2.set_yticklabels(["{:d}".format(int(x)) for x in yticks[1:-1]], fontsize=24)
    #ax2.set_ylabel('Wind Speed (knots)',fontsize=32)
    ax2.tick_params(axis='y',labelsize=30,length=8,width=2)
    fig.set_size_inches(32,9)
    plt.tight_layout()
    fig.savefig(atcfid + '/predictions/' + fname,pad=0,dpi=100)
    plt.close('all')
