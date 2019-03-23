import os
import folium
from folium.plugins import HeatMap



class Getmap:

    osu_coords = [45.8169,  -119.2850]

    def __init__(self, savename, tiles='Stamen Terrain', zoom_start = 8):
        self.savepath = os.path.join("./tmp_map/{}.html".format(savename))
        self.tiles = tiles
        self.zoom_starts = zoom_start

    def generate_basemap(self):
        self.base_map = folium.Map(location=Getmap.osu_coords, control_scale=True, zoom_start=self.zoom_starts, tiles=self.tiles)
        return self

    def add_heatmap(self, data, min_opacity=0.5, max_zoom=18, max_val=1, radius=15, blur=15, gradient = None):
        HeatMap(data=data, min_opacity=min_opacity, 
        max_zoom=max_zoom, max_val=max_val, radius=radius, blur=blur, gradient=gradient).add_to(self.base_map)

    def add_marker(self, location, *args):
        tooltip = "Click to see risk year"
        popup = "".join(args)
        folium.Marker(location, popup=popup).add_to(self.base_map)


    def add_clickmarker(self, *args):
        popup = "".join(args)
        self.base_map.add_child(folium.ClickForMarker(popup=popup))        

    def show_map(self):
        return self.base_map

    def savemap(self):
        return self.base_map.save(self.savepath)



