import os
import folium
from folium.plugins import HeatMap
import branca.colormap as cm
from folium.features import DivIcon


color_list = ['white', 'cyan', 'chartreuse','yellow',  'orange', 'red']
color_ratio = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
cmap = cm.LinearColormap(color_list, index= color_ratio)
cmap_dict = dict(zip(color_ratio, color_list))


tile_NatGeo = "https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}"
attr_NatGeo = "'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC'"

class FoliumMaps:

    osu_coords = [45.8169,  -119.2850]

    def __init__(self, savename, tiles=tile_NatGeo, attr=attr_NatGeo, zoom_start = 6):
        self.savepath = os.path.join("./static/{}.html".format(savename))
        self.tiles = tiles
        self.attr = attr
        self.zoom_starts = zoom_start

    def generate_basemap(self):
        self.base_map = folium.Map(location=FoliumMaps.osu_coords, control_scale=True, zoom_start=self.zoom_starts, tiles=self.tiles, attr = self.attr)
        return self

    def add_heatmap(self, data, min_opacity=0.6, max_zoom=15, max_val=1, radius=12, blur=10, gradient = cmap_dict):
        HeatMap(data=data, min_opacity=min_opacity, 
        max_zoom=max_zoom, max_val=max_val, radius=radius, blur=blur, gradient=gradient).add_to(self.base_map)

    def add_marker(self, location, *args):
        popup = "".join(args)
        folium.Marker(location, popup=popup).add_to(self.base_map)

    def add_circleMarker(self, location, risk, radius=15):
        popup = f"Latitude: {location[0]}, Longitude: {location[1]}\nPredict Risk Value: {risk}"
        folium.CircleMarker(location, radius=radius, color = cmap(risk), popup=popup, fill=True, fill_color = cmap(risk)).add_to(self.base_map)

    def add_text(self, location, text, risk):
        folium.Marker(location, icon=DivIcon(
            icon_size = (20, 20),
            icon_anchor = (0, 0),
            html = '<div style="font-size: 20pt; color: %s">%s</div>'% (cmap(risk), text)
        )).add_to(self.base_map)

    def add_clickmarker(self, *args):
        popup = "".join(args)
        self.base_map.add_child(folium.ClickForMarker(popup=popup))        

    def show_map(self):
        return self.base_map

    def savemap(self):
        return self.base_map.save(self.savepath)

    def getsavepath(self):
        return os.path.abspath(self.savepath)



