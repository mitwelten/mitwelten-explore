from dash_iconify import DashIconify
import dash_mantine_components as dmc
import plotly.colors
import json

with open("dashboard/data/mapbox_layers.json", "r", encoding="utf-8") as f:
    MAPBOX_LAYERS = json.loads(f.read())

with open("dashboard/data/mapbox_layers_description.json", "r", encoding="utf-8") as f:
    MAP_LAYER_DESCRIPTIONS = json.loads(f.read())

MAP_LAYERS_WITH_LEGEND = [
    k
    for k in MAP_LAYER_DESCRIPTIONS.keys()
    if MAP_LAYER_DESCRIPTIONS[k].get("img") is not None
]

DEFAULT_MAP_LAYER = {
    "below": "traces",
    "sourcetype": "raster",
    "sourceattribution": '<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
    "source": [
        "https://wmts10.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg"
    ],
}


class Icons(object):
    add_annotation = "material-symbols:add-comment-outline"
    annotation_bank = "material-symbols:comment-bank-outline"
    area_chart = "mdi:chart-areaspline-variant"
    arrow_back = "typcn:arrow-back"
    arrow_down_expand = "material-symbols:expand-more"
    arrow_right = "ic:outline-arrow-right"
    arrow_subdir = "ic:baseline-subdirectory-arrow-right"
    bar_chart = "mdi:chart-bar"
    bee = "icon-park-outline:bee"
    bird = "game-icons:seagull"
    bookmark = "material-symbols:bookmark-outline-rounded"
    burger_menu = "mingcute:menu-fill"
    copyright = "ic:baseline-copyright"
    dashboard = "ic:outline-space-dashboard"
    database = "material-symbols:database-outline"
    docs_book = "gridicons:book"
    edit_pen = "material-symbols:edit-outline-rounded"
    env_sensors = "carbon:soil-temperature-field"
    help = "material-symbols:help-outline"
    hexagon_filled = "ic:twotone-hexagon"
    hexagon_outline = "ic:outline-hexagon"
    hierarchy = "system-uicons:hierarchy"
    info = "mdi:about-variant"
    info_filled = "mdi:information"
    layout_rect = "icon-park-outline:rectangle-one"
    layout_row = "icon-park-outline:layout-two"
    license_cc = "cib:creative-commons"
    license_cc_pd = "cib:creative-commons-pd"
    license_cc0 = "cib:creative-commons-zero"
    line_chart = "mdi:chart-line"
    list_legend = "la:list-ul"
    location_marker = "material-symbols:location-on-outline"
    location_poi = "gis:location-poi"
    logout = "material-symbols:logout"
    map_chart = "material-symbols:map-outline-rounded"
    map_pin = "uil:map-pin"
    media_image = "ph:image"
    meteoswiss = "arcticons:meteoswiss"
    more_3_dots = "material-symbols:more-horiz"
    more_3_dots_vertical = "material-symbols:more-vert"
    multi_chart = "material-symbols:ssid-chart-rounded"
    multimedia = "mdi:multimedia"
    open_in_new_tab = "ic:round-open-in-new"
    pax_counter = "mdi:wireless"
    quickstart_rocket = "material-symbols:rocket-launch"
    scatter_chart = "mdi:chart-scatter-plot"
    search_location = "fa-solid:search-location"
    settings_gear = "clarity:settings-line"
    share = "material-symbols:share"
    single_chart = "material-symbols:show-chart-rounded"
    success_round = "ep:success-filled"
    switch_arrows = "mi:switch"
    sync_off = "uis:sync-slash"
    sync_on = "uil:sync"
    theme = "fluent:dark-theme-20-filled"
    trash = "mdi:trash-can-outline"
    weather = "fluent:weather-partly-cloudy-day-16-regular"
    world_explore = "ic:sharp-travel-explore"


class IconUrls(object):
    meteoswiss = "/app/assets/icons/meteoswiss.svg"
    gbif = "/app/assets/icons/gbif.png"


icon_urls = IconUrls()


icons = Icons()


def get_icon(icon=None, width=None, **kwargs):

    if "/assets/icons" in icon:
        if width:

            return dmc.Avatar(src=icon, size=width, **kwargs)
        else:
            return dmc.Avatar(src=icon, **kwargs)
    else:
        if width:
            return DashIconify(icon=icon, width=width, **kwargs)
        else:
            return DashIconify(icon=icon, **kwargs)


MULTI_VIZ_COLORSCALE = [
    "#228BE6",  # blue.6
    "#40C057",  # green.6
    "#7950F2",  # violet.6
    "#E64980",  # pink.6
    "#FD7E14",  # orange.6
    "#FAB005",  # yellow.6
    "#BE4BDB",  # grape.6
]
MULTI_VIZ_COLORSCALE_MT = [
    "blue.6",
    "green.6",
    "violet.6",
    "pink.6",
    "orange.6",
    "yellow.6",
    "grape.6",
]

SINGLE_CHART_COLOR = "#12B886"  #  #teal.6

SEQUENTIAL_COLORSCALES = [
    plotly.colors.sequential.Blues,
    plotly.colors.sequential.Blues,
    plotly.colors.sequential.Greens,
    plotly.colors.sequential.tempo,
    plotly.colors.sequential.Bluered,
    plotly.colors.diverging.Portland,
    plotly.colors.sequential.YlOrRd,
    plotly.colors.sequential.YlGnBu,
    plotly.colors.sequential.deep_r,
    plotly.colors.sequential.Viridis,
    plotly.colors.sequential.Tealgrn,
    plotly.colors.sequential.RdPu,
]

TRANSPARENT_COLORSCALE = [
    [0.0, "rgba(0,0,0,0)"],
    [1.0, "rgba(0,0,0,0)"],
]
