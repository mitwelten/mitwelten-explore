from h3 import h3
import numpy as np

def validate_coordinates(lat, lon):
    if lon < 5.5 or lon > 9:
        return False
    if lat < 46.5  or lat > 49:
        return False
    return True

def zoom_to_cell_resolution(zoom):
    # if zoom > 17.5:
    if zoom > 18.5:
        return 14
    elif 17 < zoom <= 18.5:
        return 13
    elif 16.2 < zoom <= 17:
        return 12
    elif 15.2 < zoom <= 16.2:
        return 11
    elif 14 < zoom <= 15.2:
        return 10
    elif 12.5 < zoom <= 14:
        return 9
    elif 10.5 < zoom <= 12.5:
        return 8
    else:
        return 7
    
def calculate_zoom_from_points(latmin,latmax,lonmin,lonmax):
    try:
        max_bound = max(abs(lonmax-lonmin), abs(latmax-latmin)) * 111
        if max_bound == 0:
            return 18
        return 13.7 - np.log(max_bound)
    except:
        return 18


    
def generate_clusters(resolution, lat, lon,values, fun, *args):
    assert(len(lat)==len(values)==len(lon))
    values_dict = {}
    for i in range(len(lat)):
        parent_cluster_id = h3.geo_to_h3(lat[i], lon[i], resolution)
        if not parent_cluster_id in values_dict:
            values_dict[parent_cluster_id] = []
        values_dict[parent_cluster_id].append(values[i])

    for h3_parent_id in values_dict:
        values_dict[h3_parent_id] = fun(values_dict[h3_parent_id], *args)
    return values_dict

def get_points_in_cluster(cluster_id, lat,lon,point_ids):
    assert(len(lat)==len(point_ids)==len(lon))
    resolution = h3.h3_get_resolution(cluster_id)
    points_in_cell = []
    for i in range(len(lat)):
        if h3.geo_to_h3(lat[i], lon[i], resolution) == cluster_id:
            points_in_cell.append(point_ids[i])
    return points_in_cell


def generate_geojson(unique_ids):
    geojson_features = []
    for h3id in unique_ids:
        poly = [[list(tup) for tup in h3.h3_to_geo_boundary(h3id, geo_json=True)]]
        geojson_features.append(
            {
                "type": "Feature",
                "properties": {"h3index": h3id},
                "geometry": {"coordinates": poly, "type": "Polygon"},
            }
        )

    return {"type": "FeatureCollection", "features": geojson_features}