from dash_iconify import DashIconify
import dash_mantine_components as dmc
import plotly.colors


class Icons(object):
    share = "material-symbols:share"
    add_annotation = "material-symbols:add-comment-outline"
    annotation_bank = "material-symbols:comment-bank-outline"
    bee = "icon-park-outline:bee"
    more_3_dots = "material-symbols:more-horiz"
    more_3_dots_vertical = "material-symbols:more-vert"
    line_chart = "mdi:chart-line"
    scatter_chart = "mdi:chart-scatter-plot"
    bar_chart = "mdi:chart-bar"
    area_chart = "mdi:chart-areaspline-variant"
    settings_gear = "clarity:settings-line"
    sync_on = "uil:sync"
    sync_off = "uis:sync-slash"
    location_marker = "material-symbols:location-on-outline"
    hierarchy = "system-uicons:hierarchy"
    arrow_right = "ic:outline-arrow-right"
    open_in_new_tab = "ic:round-open-in-new"
    bookmark = "material-symbols:bookmark-outline-rounded"
    dashboard = "ic:outline-space-dashboard"
    arrow_subdir = "ic:baseline-subdirectory-arrow-right"
    pax_counter = "mdi:wireless"
    meteoswiss = "arcticons:meteoswiss"
    env_sensors = "carbon:soil-temperature-field"
    help = "material-symbols:help-outline"
    info = "mdi:about-variant"
    theme = "fluent:dark-theme-20-filled"
    edit_pen = "material-symbols:edit-outline-rounded"
    layout_row = "icon-park-outline:layout-two"
    layout_rect = "icon-park-outline:rectangle-one"
    trash = "mdi:trash-can-outline"
    bird = "game-icons:seagull"
    docs_book = "gridicons:book"
    quickstart_rocket = "material-symbols:rocket-launch"
    database = "material-symbols:database-outline"
    world_explore = "ic:sharp-travel-explore"
    search_location = "fa-solid:search-location"
    arrow_back = "typcn:arrow-back"
    burger_menu = "mingcute:menu-fill"
    arrow_down_expand = "material-symbols:expand-more"
    logout = "material-symbols:logout"
    single_chart = "material-symbols:show-chart-rounded"
    multi_chart = "material-symbols:ssid-chart-rounded"
    map_chart = "material-symbols:map-outline-rounded"
    weather = "fluent:weather-partly-cloudy-day-16-regular"
    hexagon_outline = "ic:outline-hexagon"
    hexagon_filled = "ic:twotone-hexagon"
    switch_arrows = "mi:switch"
    success_round = "ep:success-filled"
    copyright = "ic:baseline-copyright"
    license_cc = "cib:creative-commons"
    license_cc_pd = "cib:creative-commons-pd"
    license_cc0 = "cib:creative-commons-zero"


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


nav_style_active = {
    "cursor": "pointer",
    "height": "39px",
    "borderBottom": "3px solid #4C6EF5",
    "borderTop": "3px solid rgba(0,0,0,0)",
}
nav_style_inactive = {
    "cursor": "pointer",
    "height": "39px",
    "borderTop": "3px solid rgba(0,0,0,0)",
}
