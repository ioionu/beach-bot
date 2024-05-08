#!/usr/bin/python

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import logging
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.markers import MarkerStyle
from matplotlib.text import TextPath
import numpy as np
from adjustText import adjust_text
import matplotlib.patches as mpatches
import re

logger = logging.getLogger("BeachBot")
logging.basicConfig(level=logging.INFO)

colours = {
    'Unlikely': 'green',
    'Likely': 'red',
    'Possible': 'orange',
    'sea': '#c9f0f2',
    'land': '#bedbcf'
}

icons = {
    'Unlikely': TextPath((0, 0), '☑'),
    'Likely': TextPath((0, 0), '☒'),
    'Possible': TextPath((0, 0), '⚠')
}

class BeachMap:
    def __init__(self, name: str, area_data: dict):
        self.name = name
        self.area_data = area_data
        logger.info(self.area_data)

    def bounds(self):
        llcrnrlon = None
        llcrnrlat = None
        urcrnrlon = None
        urcrnrlat = None
        buffer = 0.01
        for forcast in self.area_data:
            for location in self.area_data[forcast]:
                
                lat = float(location['geometry']['coordinates'][1])
                lng = float(location['geometry']['coordinates'][0])

                if llcrnrlat is None or lat < llcrnrlat:
                    llcrnrlat = lat
                if urcrnrlat is None or lat > urcrnrlat:
                    urcrnrlat = lat
                if llcrnrlon is None or lng < llcrnrlon:
                    llcrnrlon = lng
                if urcrnrlon is None or lng > urcrnrlon:
                    urcrnrlon = lng

        if llcrnrlat is None or urcrnrlat is None or llcrnrlon is None or urcrnrlon is None:
            return None
        # make bounds squarish.
        width = urcrnrlon - llcrnrlon
        height = urcrnrlat - llcrnrlat
        if width > height:
            diff = width - height
            llcrnrlat -= diff / 2
            urcrnrlat += diff / 2
        else:
            diff = height - width
            llcrnrlon -= diff / 2
            urcrnrlon += diff / 2
        return {
            "llcrnrlon": llcrnrlon - buffer,
            "llcrnrlat": llcrnrlat - buffer,
            "urcrnrlon": urcrnrlon + buffer,
            "urcrnrlat": urcrnrlat + buffer,
        }


    def add_legend(self, x):
        patches = []
        for key in ['Unlikely', 'Possible', 'Likely']:
            patches.append(mpatches.Patch(color=colours[key], label=key))
        x.legend(handles=patches, loc='upper left')
        return x

    def add_markers(self, map):
        texts = []
        for forcast in self.area_data:
            for location in self.area_data[forcast]:            
                lat = float(location['geometry']['coordinates'][1])
                lng = float(location['geometry']['coordinates'][0])
                map.scatter(
                    x=lng,
                    y=lat,
                    latlon=True,
                    marker=MarkerStyle(icons[location['properties']['pollutionForecast']]).scaled(2.0),
                    color=colours[forcast],
                    zorder=2
                )
                xx, yy = map(lng, lat)
                texts.append(
                    plt.text(
                        x=xx,
                        y=yy,
                        s=location['properties']['siteName'],
                        fontsize=10,
                        fontweight='bold'
                    )
                )

        adjust_text(texts, arrowprops=dict(arrowstyle='->', color='black'))

    def get_file_name(self):
        safe_name = re.sub(r'[-\s]+', '-', self.name.lower())
        file_name = "/tmp/map-{name}.png".format(name=safe_name)
        return file_name

    def draw_map(self):
        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(111)

        bb = self.bounds()
        if bb is None:
            return None
        m = Basemap(projection='merc',
            llcrnrlon=bb['llcrnrlon'],
            llcrnrlat=bb['llcrnrlat'],
            urcrnrlon=bb['urcrnrlon'],
            urcrnrlat=bb['urcrnrlat'],
            lat_ts=20,
            resolution='c'
        )
        m.readshapefile('nsw/nsw', 'nsw', drawbounds=False)
        m.drawmapboundary(fill_color=colours['sea'])
        plt.title(self.name)

        patches   = []

        for shape in m.nsw:
            patches.append( Polygon(np.array(shape)) )
                
        ax.add_collection(PatchCollection(
            patches,
            facecolor=colours['land'], 
            linewidths=0, 
            zorder=1
        ))

        self.add_markers(m)

        self.add_legend(ax)

        file_name = self.get_file_name()
        # plt.show()
        plt.savefig(file_name)
        return file_name
