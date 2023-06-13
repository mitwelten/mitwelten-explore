import plotly.graph_objects as go
from dashboard.styles import MULTI_VIZ_COLORSCALE
import pandas as pd
from plotly.subplots import make_subplots
import datetime
import re

rdbu_colors = [
    [0.0, "#F03E3E"],
    [0.499, "white"],
    [0.5, "rgba(0,0,0,0)"],
    [0.501, "white"],
    [1.0, "#364FC7"],
]

fft_tick_values = [
    365 * 24 * 3600,
    91 * 24 * 3600,
    30 * 24 * 3600,
    7 * 24 * 3600,
    2 * 24 * 3600,
    24 * 3600,
    12 * 3600,
#    8 * 3600,
    6 * 3600,
#    2 * 3600,
]
fft_tick_labels = [
    "1 Year",
    "3 Months",
    "1 Month",
    "1 Week",
    "2 Days",
    "1 Day",
    "12 Hour",
#    "8 Hour",
    "6 Hour",
#    "2 Hour",
]


def correlation_matrix_heatmap(matrix, labels, light_mode=True):
    z = [c[1:] for c in matrix[:-1]]
    text = [[f"{zj:.2f}" if zj != 0 else "" for zj in zi] for zi in z]
    ylabels = labels[:-1]
    xlabels = labels[1:]
    xlabels_short = [re.split(r" |:",str(x))[0] for x in xlabels]
    ylabels_short = [re.split(r" |:",str(x))[0] for x in ylabels]
    try:
        xlabels_short = [f"{xlabels_short[i]}<br><sup>{xlabels[i].split(xlabels_short[i])[1]}</sup>" for i in range(len(xlabels))]
        ylabels_short = [f"{ylabels_short[i]}<br><sup>{ylabels[i].split(ylabels_short[i])[1]}</sup>" for i in range(len(ylabels))]
    except:
        pass
    ylabels_idx = [i for i in range(len(labels)-1)]
    xlabels_idx = [i for i in range(len(labels)-1)]
    hovertemplate_matrix = []
    for y in ylabels:
        ylist = []
        for x in xlabels:
            ylist.append(f"{y}<br>{x}")

        hovertemplate_matrix.append(ylist)


        
    fig = make_subplots(
        cols=2,
        rows=2,
        shared_xaxes=True,
        shared_yaxes=True,
        vertical_spacing=0,
        horizontal_spacing=0,
        column_widths=[0.35, 0.65],
        row_heights=[0.9, 0.1],
    )
    fig.add_trace(
        go.Heatmap(
            z=z,
            text=text,
            texttemplate="%{text}",
            x=xlabels_idx,
            y=ylabels_idx,
            customdata=hovertemplate_matrix,
            colorscale=rdbu_colors,
            zmid=0,
            zmax=1,
            zmin=-1,
            ygap=2,
            xgap=2,
            hovertemplate="<sup>Datasets</sup><br><i>%{customdata}</i> <br>Pearson Coefficient: <b>%{text}</b><extra></extra>",
            showlegend=False,
            colorbar_title="Pearson correlation coefficient",
            colorbar_title_side="right",
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=[-1 for i in range(len(ylabels))],
            y=ylabels_idx,
            text=ylabels_short,
            customdata=ylabels,
            mode="text",
            showlegend=False,
            textfont=dict(color=MULTI_VIZ_COLORSCALE, size=13),
            textposition="middle center",
            hovertemplate="%{customdata}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            y=[-1 for i in range(len(xlabels))],
            x=xlabels_idx,
            text=xlabels_short,
            customdata=xlabels,
            mode="text",
            textfont=dict(color=MULTI_VIZ_COLORSCALE[1:], size=13),
            showlegend=False,
            hovertemplate="%{customdata}<extra></extra>",
        ),
        row=2,
        col=2,
    )
    fig.update_yaxes(visible=False)
    fig.update_xaxes(visible=False)
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        template="plotly_white" if light_mode else "plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def fft_single(amplitude, periods_s, light_mode):
    print(amplitude[0], periods_s[0])
    fig = go.Figure()
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        template="plotly_white" if light_mode else "plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.add_trace(
        go.Scatter(
            x=periods_s,  # [:max(peaks_index)*2],
            y=amplitude,  # [:max(peaks_index)*2],
            mode="lines",
            line_width=1.5,
            opacity=1,
            customdata=[None] + [str(datetime.timedelta(seconds=f)) for f in periods_s],
            hovertemplate="<b>Period: %{customdata}</b><br>Amplitude: %{y} <br><extra></extra>",
            showlegend=False,
        )
    )
    fig.update_xaxes(type="log", autorange="reversed",ticktext=fft_tick_labels, tickvals=fft_tick_values, )
    fig.update_yaxes(type="log")

    return fig

def fft_multi(data,dataset_names = None, light_mode=True):
    # data[0] : [[time string list],[values_list]]
    if dataset_names is not None:
        if len(dataset_names) == len(data):
            dataset_names = [d.split(" ")[0] for d in dataset_names]
        else:
            dataset_names = None
        
    fig = go.Figure()
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        template="plotly_white" if light_mode else "plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend_orientation="h"
    )
    for i in range(len(data)):
    
        fig.add_trace(
            go.Scatter(
                x=data[i][0],  # [:max(peaks_index)*2],
                y=data[i][1],  # [:max(peaks_index)*2],
                mode="lines",
                line_color = MULTI_VIZ_COLORSCALE[i],
                line_width=2,
                opacity=.8,
                customdata=[str(datetime.timedelta(seconds=f)) for f in data[i][0]],
                hovertemplate="<b>Period: %{customdata}</b><br>Amplitude: %{y} <br><extra></extra>",
                showlegend=False if dataset_names is None else True,
                name = dataset_names[i] if dataset_names is not None else None
            )
        )
    fig.update_xaxes(type="log", autorange="reversed",ticktext=fft_tick_labels, tickvals=fft_tick_values, )
    fig.update_yaxes(type="log")

    return fig