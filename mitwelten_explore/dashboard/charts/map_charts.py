import plotly.graph_objects as go
from dashboard.utils.geo_utils import (
    generate_geojson,
    calculate_zoom_from_points,
    zoom_to_cell_resolution,
    generate_clusters,
)
import numpy as np
from configuration import DEFAULT_LAT, DEFAULT_LON, DEFAULT_ZOOM
from dashboard.styles import MULTI_VIZ_COLORSCALE


# empty map
def generate_empty_map(zoom=DEFAULT_ZOOM, clat=DEFAULT_LAT, clon=DEFAULT_LON):
    fig = go.Figure(go.Choroplethmapbox())
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox={
            "style": "white-bg",
            "zoom": zoom,
            "center": {"lat": clat, "lon": clon},
            "layers": [
                {
                    "below": "traces",
                    "sourcetype": "raster",
                    "sourceattribution": '<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
                    "source": [
                        "https://wmts10.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg"
                    ],
                },
            ],
        },
        showlegend=False,
    )
    return fig


# single points, highlight
def generate_scatter_map_plot(lats, lons, names, ids, selected=None):

    if len(lats) == 0:
        mean_lat = DEFAULT_LAT
        mean_lon = DEFAULT_LON
    else:
        not_0_lats = [lat for lat in lats if lat !=0.0]
        not_0_lons = [lon for lon in lons if lon !=0.0]
        mean_lat = np.mean(not_0_lats)
        mean_lon = np.mean(not_0_lons)
    fig = go.Figure()
    if selected is not None:
        if isinstance(selected, list):
            for sel in selected:
                selected_index = ids.index(sel)
                fig.add_trace(
                    go.Scattermapbox(
                        lon=[lons[selected_index]],
                        lat=[lats[selected_index]],
                        text=[names[selected_index]],
                        customdata=[ids[selected_index]],
                        marker={"size": 25, "color": "#FA5252", "opacity": 0.7},
                        hovertemplate="%{text}<extra></extra>",
                    )
                )
        else:
            selected_index = ids.index(selected)
            fig.add_trace(
                go.Scattermapbox(
                    lon=[lons[selected_index]],
                    lat=[lats[selected_index]],
                    text=[names[selected_index]],
                    customdata=[ids[selected_index]],
                    marker={"size": 25, "color": "#FA5252", "opacity": 0.7},
                    hovertemplate="%{text}<extra></extra>",
                )
            )
    fig.add_trace(
        go.Scattermapbox(
            lon=lons,
            lat=lats,
            text=names,
            customdata=ids,
            marker={"size": 15, "color": "#4C6EF5", "opacity": 0.9},
            hovertemplate="%{text}<extra></extra>",
        )
    )

    fig.update_layout(
        clickmode="event+select",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel_bgcolor="rgba(245, 245, 245,0.8)",
        mapbox={
            "style": "open-street-map",
            "center": {"lon": mean_lon, "lat": mean_lat},
            "zoom": 10,
        },
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig


def generate_multi_scatter_map_plot(data:list):
    if data is None or len(data)==0:
        return generate_empty_map()
    traces = []
    lats = []
    lons = []
    
    for i in range(len(data)):

        traces.append(
            go.Scattermapbox(
                    lon=data[i].get("longitude"),
                    lat=data[i].get("latitude"),
                    text=data[i].get("name"),
                    customdata=data[i].get("id"),
                    marker={"size": 15, "color": MULTI_VIZ_COLORSCALE[i], "opacity": 0.8},
                    hovertemplate="%{text}<extra></extra>",
                )
        )
        lons+=data[i].get("longitude")
        lats+=data[i].get("latitude")

    

    fig = go.Figure()
    for trace in traces:
        fig.add_trace(trace)

    lats = [l for l in lats if l >40]
    lons = [l for l in lons if l >1]
    zoom = calculate_zoom_from_points(min(lats),max(lats),min(lons),max(lons))
    center_lat = (max(lats)+min(lats))/2
    center_lon = (max(lons)+min(lons))/2


    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel_bgcolor="rgba(245, 245, 245,0.8)",
        mapbox={
            "style": "white-bg",
            "zoom": zoom,
            "center": {"lat": center_lat, "lon": center_lon},
            "layers": [
                {
                    "below": "traces",
                    "sourcetype": "raster",
                    "sourceattribution": '<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
                    "source": [
                        "https://wmts10.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg"
                    ],
                },
            ],
        },
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    fig.update_traces(cluster_enabled=True, cluster_size=10, cluster_opacity=0.8,cluster_maxzoom=20) # https://plotly.com/python/reference/scattermapbox/#scattermapbox-cluster
    return fig


def generate_choroplethmap(h3ids, values):
    return go.Choroplethmapbox(
        geojson=generate_geojson(h3ids),
        z=values,
        text=values,
        locations=h3ids,
        customdata=[{"n_deployments": d, "type": "cell"} for d in values],
        featureidkey="properties.h3index",
        colorscale="Tealgrn",
        marker_opacity=0.5,
        marker_line_width=1.5,
        marker_line_color="rgba(0,0,0,1)",
        hovertemplate="Count: <b>%{z}</b><extra></extra>",
        showscale=True,
        colorbar=go.choroplethmapbox.ColorBar(
            thicknessmode="pixels",
            thickness=15,
            x=0.99,
            y=0.99,
            yanchor="top",
            ypad=8,
            xpad=8,
            len=0.5,
            bgcolor="rgba(245, 245, 245,0.8)",
            xanchor="right",
            outlinecolor="rgba(245, 245, 245,0)",
        ),
    )


def generate_scattermap(lat, lon, ids, color="blue", size=7):
    return go.Scattermapbox(
        lon=lon,
        lat=lat,
        text=ids,
        mode="markers",
        customdata=[{"id": d, "type": "point"} for d in ids],
        marker={"size": size, "color": color, "opacity": 0.7},
        # hovertemplate="Deployment %{text}<br>Type: %{customdata}<extra></extra>",
    )


def generate_h3hexbin_map(
    lat, lon, values, ids, zoom=None, clat=None, clon=None, aggregate_fun=np.sum
):
    if len(lat) == 0:
        return generate_empty_map(
            zoom=zoom if zoom else DEFAULT_ZOOM,
            clat=clat if clat else DEFAULT_LAT,
            clon=clon if clon else DEFAULT_LON,
        )
    lat_min = np.min(lat)
    lat_max = np.max(lat)
    lon_min = np.min(lon)
    lon_max = np.max(lon)
    if zoom == None:
        zoom = calculate_zoom_from_points(lat_min, lat_max, lon_min, lon_max)

    if clat is None:

        if len(lat) > 1:
            clat = (lat_max + lat_min) / 2
            clon = (lon_max + lon_min) / 2
        else:
            clat = lat_max
            clon = lon_max
    resolution = zoom_to_cell_resolution(zoom)
    aggregated = generate_clusters(
        resolution=resolution, lat=lat, lon=lon, values=values, fun=aggregate_fun
    )
    locations = list(aggregated.keys())
    values = list(aggregated.values())
    hexbin_map = go.Figure()

    if resolution > 7:
        lat_m = []
        lat_g = []
        lon_m = []
        lon_g = []
        ids_m = []
        ids_g = []
        for i in range(len(ids)):
            if isinstance(ids[i], str) and ids[i].startswith("g"):
                lat_g.append(lat[i])
                lon_g.append(lon[i])
                ids_g.append(ids[i])
            else:
                lat_m.append(lat[i])
                lon_m.append(lon[i])
                ids_m.append(ids[i])

        if len(ids_g) > 0:

            hexbin_map.add_trace(generate_scattermap(lat_g, lon_g, ids_g, "#AE3EC9", 6))
        if len(ids_m) > 0:
            hexbin_map.add_trace(generate_scattermap(lat_m, lon_m, ids_m, "#F03E3E", 8))
    if resolution <= 13:
        hexbin_map.add_trace(generate_choroplethmap(locations, values))
    hexbin_map.update_layout(
        clickmode="event",
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel_bgcolor="rgba(245, 245, 245,0.8)",
        mapbox={
            "style": "white-bg",
            "zoom": zoom,
            "center": {"lat": clat, "lon": clon},
            "layers": [
                {
                    "below": "traces",
                    "sourcetype": "raster",
                    "sourceattribution": '<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
                    "source": [
                        "https://wmts10.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg"
                    ],
                },
            ],
        },
        showlegend=False,
    )
    return hexbin_map
