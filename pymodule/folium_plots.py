import folium
import geopandas as gpd
from shapely.geometry import Polygon



def create_folium_polygon(coords):


    # Create the polygon
    polygon = Polygon(coords)

    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame([1], geometry=[polygon], crs='EPSG:2262')  # NY State Plane East

    # Convert to lat/lon for web mapping
    gdf_web = gdf.to_crs('EPSG:4326')

    # Get the centroid for map center
    center_lat = gdf_web.geometry.centroid.y.iloc[0]
    center_lon = gdf_web.geometry.centroid.x.iloc[0]

    # Create folium map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

    return m
