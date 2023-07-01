import plotly.graph_objects as go
import plotly.colors
from dashboard.utils.geo_utils import (
    generate_geojson,
    calculate_zoom_from_points,
    zoom_to_cell_resolution,
    generate_clusters,
    validate_coordinates,
)
import numpy as np
from configuration import DEFAULT_LAT, DEFAULT_LON, DEFAULT_ZOOM
from dashboard.styles import (
    MULTI_VIZ_COLORSCALE,
    SEQUENTIAL_COLORSCALES,
    TRANSPARENT_COLORSCALE,
)


colors1, _ = plotly.colors.convert_colors_to_same_type(SEQUENTIAL_COLORSCALES[0])
colors2, _ = plotly.colors.convert_colors_to_same_type(SEQUENTIAL_COLORSCALES[1])
colorscale1 = plotly.colors.make_colorscale(colors1)
colorscale2 = plotly.colors.make_colorscale(colors2)

SWISSTOPO_LAYER = [
    {
        "below": "traces",
        "sourcetype": "raster",
        "sourceattribution": '<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
        "source": [
            "https://wmts10.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg"
        ],
    },
]


class LocationData:
    def __init__(
        self, lat=[], lon=[], values=[], ids=[], name=None, agg_fcn="sum", visible=True
    ):
        self.lat = lat
        self.lon = lon
        self.values = values
        self.ids = ids
        self.name = name
        self.agg_fcn = agg_fcn
        self.visible = visible

    def to_dict(self):
        return dict(
            lat=self.lat,
            lon=self.lon,
            values=self.values,
            ids=self.ids,
            name=self.name,
            agg_fcn=self.agg_fcn,
            visible=self.visible,
        )

    def add_datapoint(self, lat, lon, value, id):
        self.lat.append(lat)
        self.lon.append(lon)
        self.values.append(value)
        self.ids.append(id)

    def sort(self, descending=False):
        sorted_data = sorted(
            zip(self.values, self.lon, self.lat, self.ids), reverse=descending
        )
        self.values, self.lon, self.lat, self.ids = zip(*sorted_data)


def agg_fcn_mapper(fcn):
    if fcn == "mean":
        return np.mean
    elif fcn == "sum":
        return np.sum
    elif fcn == "min":
        return np.min
    elif fcn == "max":
        return np.max
    elif fcn == "median":
        return np.median
    else:
        return np.mean


def get_continuous_color(colorscale, intermed):
    """
    Plotly continuous colorscales assign colors to the range [0, 1]. This function computes the intermediate
    color for any value in that range.

    Plotly doesn't make the colorscales directly accessible in a common format.
    Some are ready to use:

        colorscale = plotly.colors.PLOTLY_SCALES["Greens"]

    Others are just swatches that need to be constructed into a colorscale:

        viridis_colors, scale = plotly.colors.convert_colors_to_same_type(plotly.colors.sequential.Viridis)
        colorscale = plotly.colors.make_colorscale(viridis_colors, scale=scale)

    :param colorscale: A plotly continuous colorscale defined with RGB string colors.
    :param intermed: value in the range [0, 1]
    :return: color in rgb string format
    :rtype: str
    """
    if len(colorscale) < 1:
        raise ValueError("colorscale must have at least one color")

    if intermed <= 0 or len(colorscale) == 1:
        return colorscale[0][1]
    if intermed >= 1:
        return colorscale[-1][1]

    for cutoff, color in colorscale:
        if intermed > cutoff:
            low_cutoff, low_color = cutoff, color
        else:
            high_cutoff, high_color = cutoff, color
            break

    # noinspection PyUnboundLocalVariable
    return plotly.colors.find_intermediate_color(
        lowcolor=low_color,
        highcolor=high_color,
        intermed=((intermed - low_cutoff) / (high_cutoff - low_cutoff)),
        colortype="rgb",
    )


# empty map
def generate_empty_map(zoom=DEFAULT_ZOOM, clat=DEFAULT_LAT, clon=DEFAULT_LON):
    fig = go.Figure(go.Choroplethmapbox())
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox={
            "style": "white-bg",
            "zoom": zoom,
            "center": {"lat": clat, "lon": clon},
            "layers": SWISSTOPO_LAYER,
        },
        showlegend=False,
    )
    return fig


# single points, highlight
def generate_scatter_map_plot(lats, lons, names, ids, selected=None):

    valid_lats = []
    valid_lons = []
    for i in range(len(lats)):
        if validate_coordinates(lats[i], lons[i]):
            valid_lats.append(lats[i])
            valid_lons.append(lons[i])
    if len(valid_lats) == 0:
        mean_lat = DEFAULT_LAT
        mean_lon = DEFAULT_LON
        zoom = 10
    elif len(valid_lats) == 1:
        mean_lat = valid_lats[0]
        mean_lon = valid_lons[0]
        zoom = 18
    else:
        mean_lat = np.mean(valid_lats)
        mean_lon = np.mean(valid_lons)
        zoom = calculate_zoom_from_points(
            min(valid_lats), max(valid_lats), min(valid_lons), max(valid_lons)
        )
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
            "zoom": zoom,
        },
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig


def generate_multi_scatter_map_plot(data: list):
    if data is None or len(data) == 0:
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
        lons += data[i].get("longitude")
        lats += data[i].get("latitude")

    fig = go.Figure()
    for trace in traces:
        fig.add_trace(trace)

    lats = [l for l in lats if l > 40]
    lons = [l for l in lons if l > 1]
    zoom = calculate_zoom_from_points(min(lats), max(lats), min(lons), max(lons))
    center_lat = (max(lats) + min(lats)) / 2
    center_lon = (max(lons) + min(lons)) / 2

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel_bgcolor="rgba(245, 245, 245,0.8)",
        mapbox={
            "style": "white-bg",
            "zoom": zoom,
            "center": {"lat": center_lat, "lon": center_lon},
            "layers": SWISSTOPO_LAYER,
        },
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    fig.update_traces(
        cluster_enabled=True, cluster_size=10, cluster_opacity=0.8, cluster_maxzoom=20
    )  # https://plotly.com/python/reference/scattermapbox/#scattermapbox-cluster
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


def generate_scattermap(lat, lon, ids, color="blue", size=7, opacity=0.7):
    return go.Scattermapbox(
        lon=lon,
        lat=lat,
        text=ids,
        mode="markers",
        customdata=[{"id": d, "type": "point"} for d in ids],
        marker={"size": size, "color": color, "opacity": opacity},
        showlegend=False,
        hoverinfo="skip"
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
            "layers": SWISSTOPO_LAYER,
        },
        showlegend=False,
    )
    return hexbin_map


def generate_choroplethmap_label_overlay(h3ids, legends):
    geojson = generate_geojson(h3ids)

    return go.Choroplethmapbox(
        geojson=geojson,
        z=[0 for i in range(len(h3ids))],
        text=legends,
        locations=h3ids,
        featureidkey="properties.h3index",
        colorscale=TRANSPARENT_COLORSCALE,
        marker_opacity=0,
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
        showscale=False,
    )


def generate_choroplethmap_multi(
    h3ids,
    values,
    name=None,
    colorscale=colorscale1,
    borderonly=False,
    zmin=None,
    zmax=None,
):
    geojson = generate_geojson(h3ids)
    zmin = zmin if zmin is not None else min(values)
    zmax = zmax if zmax is not None else max(values)
    marker_line_color = (
        [
            get_continuous_color(
                colorscale,
                intermed=(v - zmin) / (zmax - zmin) if (zmax - zmin) > 0 else 0,
            )
            if v is not None
            else "rgba(0,0,0,0)"
            for v in values
        ]
        if borderonly
        else "rgba(0,0,0,1)"
    )
    marker_opacity = 1 if borderonly else 0.7
    marker_line_width = 4 if borderonly else 0
    m_colorscale = TRANSPARENT_COLORSCALE if borderonly else colorscale
    return go.Choroplethmapbox(
        geojson=geojson,
        z=values,
        text=values,
        locations=h3ids,
        name=name,
        customdata=[{"n_deployments": d, "type": "cell"} for d in values],
        featureidkey="properties.h3index",
        colorscale=m_colorscale,
        zmin=zmin,
        zmax=zmax,
        marker_opacity=marker_opacity,
        marker_line_width=marker_line_width,
        marker_line_color=marker_line_color,
        hovertemplate=str(name) + ": <b>%{z}</b><extra></extra>",
        showlegend=False,
        showscale=False,
    )


def colorbar_trace(
    cmin, cmax, position="top", colorscale=colorscale1, title="trace", subtitle=""
):
    colorbar_dict = dict(
        thicknessmode="pixels",
        thickness=15,
        # x=0.99,
        # y=0.99 if position == "top" else 0.01,
        # yanchor="top" if position == "top" else "bottom",
        # xanchor="right",
        # next to each other
        # xanchor="right" if position == "top" else "left",
        # yanchor="top",
        # x=0.91,
        # y=0.99,
        # left-right
        xanchor="left" if position == "top" else "right",
        x=0.005 if position == "top" else 0.995,
        y=0.995,
        yanchor="top",
        ypad=8,
        xpad=8,
        len=0.5,
        bgcolor="rgba(245, 245, 245,0.8)",
        outlinecolor="rgba(245, 245, 245,0)",
        title=f"{title}<br><sup>{subtitle}</sup>",
    )
    return go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(
            colorscale=colorscale,
            showscale=True,
            cmin=cmin,
            cmax=cmax,
            colorbar=colorbar_dict,
        ),
        showlegend=False,
        hoverinfo="none",
    )


def generate_multi_h3hexbin_map(
    ds0: LocationData,
    ds1: LocationData,
    zoom=None,
    clat=None,
    clon=None,
    scatter=False,
    range0=None,
    range1=None,
):
    ds0_visible = ds0.visible
    ds1_visible = ds1.visible
    if len(ds0.values) == 0:
        ds0_visible = False
    if len(ds1.values) == 0:
        ds1_visible = False
    if ds1_visible is False and ds0_visible is False:
        return generate_empty_map()
    concat_lats = ds0.lat + ds1.lat
    concat_lons = ds0.lon + ds1.lon
    if len(concat_lats) == 0 or len(concat_lons) == 0:
        return generate_empty_map()

    lat_min = np.min(concat_lats)
    lat_max = np.max(concat_lats)
    lon_min = np.min(concat_lons)
    lon_max = np.max(concat_lons)
    zoom = (
        calculate_zoom_from_points(lat_min, lat_max, lon_min, lon_max)
        if zoom is None
        else zoom
    )
    if clat is None:

        if len(concat_lats) > 1:
            clat = (lat_max + lat_min) / 2
            clon = (lon_max + lon_min) / 2
        else:
            clat = lat_max
            clon = lon_max

    resolution = zoom_to_cell_resolution(zoom)

    aggregated0 = generate_clusters(
        resolution=resolution,
        lat=ds0.lat,
        lon=ds0.lon,
        values=ds0.values,
        fun=agg_fcn_mapper(ds0.agg_fcn),
    )

    locations0 = list(aggregated0.keys())
    values0 = list(aggregated0.values())

    aggregated1 = generate_clusters(
        resolution=resolution,
        lat=ds1.lat,
        lon=ds1.lon,
        values=ds1.values,
        fun=agg_fcn_mapper(ds1.agg_fcn),
    )
    aggregated1 = dict(sorted(aggregated1.items(), key=lambda item: item[1]))
    locations1 = list(aggregated1.keys())
    values1 = list(aggregated1.values())
    label_dict = aggregated0.copy()
    for l in label_dict.keys():
        label_dict[l] = f"{ds0.name}: <b>{label_dict[l]}</b><br>"
    for l in aggregated1.keys():
        if l in label_dict:
            label_dict[l] += f"{ds1.name}: <b>{aggregated1[l]}</b>"
        else:
            label_dict[l] = f"<br>{ds1.name}: <b>{aggregated1[l]}</b>"

    hover_locations = list(label_dict.keys())
    hover_labels = list(label_dict.values())

    hexbin_map = go.Figure()

    if ds0_visible and len(ds0.values) > 0:
        zmin = min(values0)
        zmax = max(values0)
        zspan = zmax - zmin
        if isinstance(range0, list) and len(range0) == 2:
            zmax = int(zmin + (range0[1] / 100) * zspan)
            zmin += int((range0[0] / 100) * zspan)

        hexbin_map.add_trace(
            generate_choroplethmap_multi(
                locations0,
                values0,
                name=ds0.name,
                colorscale=colorscale1,
                zmin=zmin,
                zmax=zmax,
            )
        )
        hexbin_map.add_trace(
            colorbar_trace(
                zmin,
                zmax,
                title=ds0.name.split(" ")[0],
                subtitle=" ".join(ds0.name.split(" ")[1:]),
                colorscale=colorscale1,
            )
        )
    if ds1_visible and len(ds1.values) > 0:
        zmin = min(values1)
        zmax = max(values1)
        zspan = zmax - zmin
        if isinstance(range1, list) and len(range1) == 2:
            zmax = int(zmin + (range1[1] / 100) * zspan)
            zmin += int((range1[0] / 100) * zspan)

        hexbin_map.add_trace(
            generate_choroplethmap_multi(
                locations1,
                values1,
                name=ds1.name,
                borderonly=True,
                colorscale=colorscale2,
                zmin=zmin,
                zmax=zmax,
            )
        )
        hexbin_map.add_trace(
            colorbar_trace(
                zmin,
                zmax,
                "bottom",
                title=ds1.name.split(" ")[0],
                subtitle=" ".join(ds1.name.split(" ")[1:]),
                colorscale=colorscale2,
            )
        )
    if ds0_visible and ds1_visible:
        hexbin_map.add_trace(
            generate_choroplethmap_label_overlay(hover_locations, legends=hover_labels)
        )
    if scatter:
        if ds0_visible and len(ds0.values) > 0:
            hexbin_map.add_trace(
                generate_scattermap(ds0.lat, ds0.lon, ds0.ids, "black", 10, opacity=0.5)
            )
            hexbin_map.add_trace(
                generate_scattermap(
                    ds0.lat, ds0.lon, ds0.ids, MULTI_VIZ_COLORSCALE[0], 8
                )
            )
        if ds1_visible and len(ds1.values) > 0:
            hexbin_map.add_trace(
                generate_scattermap(ds1.lat, ds1.lon, ds1.ids, "black", 10, opacity=0.5)
            )
            hexbin_map.add_trace(
                generate_scattermap(
                    ds1.lat, ds1.lon, ds1.ids, MULTI_VIZ_COLORSCALE[1], 7, opacity=1
                )
            )

    hexbin_map.update_xaxes(visible=False)
    hexbin_map.update_yaxes(visible=False)
    hexbin_map.update_layout(
        clickmode="event",
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel_bgcolor="rgba(245, 245, 245,0.8)",
        mapbox={
            "style": "white-bg",
            "zoom": zoom,
            "center": {"lat": clat, "lon": clon},
            "layers": SWISSTOPO_LAYER,
        },
        showlegend=True,
        legend=dict(
            itemsizing="constant",
            orientation="h",
            x=0.01,
            y=0.01,
            xanchor="left",
            yanchor="bottom",
            bgcolor="rgba(245, 245, 245,0.8)",
        ),
    )
    return hexbin_map


def generate_bubblemap_trace(
    lat, lon, ids, values, color="blue", sizeref=9, opacity=0.7
):
    colorlist = []
    scaled_values = [np.sqrt(v) for v in values]
    for i in range(len(values)):
        colorlist.append("rgba(0,0,0,0.65)")
        colorlist.append(color)
    lat = [val for val in lat for _ in (0, 1)]
    lon = [val for val in lon for _ in (0, 1)]
    ids = [val for val in ids for _ in (0, 1)]
    sizeref = 2.0 * max(scaled_values) / (60**2)

    vals = []
    for v in scaled_values:
        vals.append(max(v * 1.3, 21 * sizeref))
        vals.append(max(v, 14 * sizeref))

    return go.Scattermapbox(
        lon=lon,
        lat=lat,
        text=ids,
        mode="markers",
        customdata=[{"id": d, "type": "point"} for d in ids],
        marker=dict(
            size=vals,
            color=colorlist,
            sizeref=sizeref,
            sizemode="area",
            opacity=opacity,
            allowoverlap=False,
        ),
        showlegend=False,
        hoverinfo="skip",
    )


def generate_bubblemap_hovertrace(lat, lon, ids, values, name=None, color="gray"):
    return go.Scattermapbox(
        lon=lon,
        lat=lat,
        text=values,
        name=name,
        mode="markers",
        marker=dict(opacity=0, color=color),
        hovertemplate="<b>%{text}</b>",
        showlegend=False,
    )


def generate_multi_bubble_map(
    ds0: LocationData,
    ds1: LocationData,
    zoom=None,
    clat=None,
    clon=None,
):
    ds0_visible = ds0.visible
    ds1_visible = ds1.visible
    if len(ds0.values) == 0:
        ds0_visible = False
    if len(ds1.values) == 0:
        ds1_visible = False
    if ds1_visible is False and ds0_visible is False:
        return generate_empty_map()
    concat_lats = ds0.lat + ds1.lat
    concat_lons = ds0.lon + ds1.lon
    if len(concat_lats) == 0 or len(concat_lons) == 0:
        return generate_empty_map()

    lat_min = np.min(concat_lats)
    lat_max = np.max(concat_lats)
    lon_min = np.min(concat_lons)
    lon_max = np.max(concat_lons)
    zoom = (
        calculate_zoom_from_points(lat_min, lat_max, lon_min, lon_max)
        if zoom is None
        else zoom
    )
    if clat is None:

        if len(concat_lats) > 1:
            clat = (lat_max + lat_min) / 2
            clon = (lon_max + lon_min) / 2
        else:
            clat = lat_max
            clon = lon_max

    resolution = zoom_to_cell_resolution(zoom)
    bubble_map = go.Figure()

    if ds0_visible and len(ds0.values) > 0:
        ds0.sort(descending=True)
        bubble_map.add_trace(
            generate_bubblemap_trace(
                lat=ds0.lat,
                lon=ds0.lon,
                ids=ds0.ids,
                values=ds0.values,
                color=MULTI_VIZ_COLORSCALE[0],
            )
        )
        bubble_map.add_trace(
            generate_bubblemap_hovertrace(
                ds0.lat,
                ds0.lon,
                ds0.ids,
                ds0.values,
                name=ds0.name,
                color=MULTI_VIZ_COLORSCALE[0],
            )
        )

    if ds1_visible and len(ds1.values) > 0:
        ds1.sort(descending=True)
        bubble_map.add_trace(
            generate_bubblemap_trace(
                lat=ds1.lat,
                lon=ds1.lon,
                ids=ds1.ids,
                values=ds1.values,
                color=MULTI_VIZ_COLORSCALE[1],
            )
        )
        bubble_map.add_trace(
            generate_bubblemap_hovertrace(
                ds1.lat,
                ds1.lon,
                ds1.ids,
                ds1.values,
                name=ds1.name,
                color=MULTI_VIZ_COLORSCALE[1],
            )
        )

    bubble_map.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel_bgcolor="rgba(245, 245, 245,0.8)",
        mapbox={
            "style": "white-bg",
            "zoom": zoom,
            "center": {"lat": clat, "lon": clon},
            "layers": SWISSTOPO_LAYER,
        },
        showlegend=False,
    )
    return bubble_map
