import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dashboard.styles import MULTI_VIZ_COLORSCALE
import pandas as pd


def minute_to_tod(minutes):
    hours, minute = divmod(minutes, 60)

    return f"{hours:02d}:{minute:02d}"


tod_tickvalues = [i * 60 for i in range(24)]
tod_ticklabels = [minute_to_tod(v) for v in tod_tickvalues]


def empty_figure():
    fig = go.Figure()
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def generate_ts_figure(
    times,
    values,
    date_from,
    date_to,
    light_mode=True,
    marker_color=None,
    chart_type="line",
):
    fig = go.Figure()
    if chart_type == "line":
        fig.add_trace(
            go.Scatter(x=times, y=values, marker_color=marker_color, mode="lines")
        )
    elif chart_type == "scatter":
        fig.add_trace(
            go.Scattergl(x=times, y=values, marker_color=marker_color, mode="markers")
        )
    elif chart_type == "area":
        fig.add_trace(
            go.Scatter(
                x=times,
                y=values,
                marker_color=marker_color,
                mode="lines",
                fill="tozeroy",
            )
        )
    elif chart_type == "bar":
        if len(times) < 250:
            fig.add_trace(go.Bar(x=times, y=values, marker_color=marker_color))
        else:
            # create scattergl lines
            times_scatter = []
            values_scatter = []
            for i in range(len(times)):
                times_scatter.append(times[i])
                times_scatter.append(times[i])
                times_scatter.append(None)
                values_scatter.append(0)
                values_scatter.append(values[i])
                values_scatter.append(None)
            fig.add_trace(
                go.Scattergl(
                    x=times_scatter,
                    y=values_scatter,
                    marker_color=marker_color,
                    mode="lines",
                )
            )

    fig.update_layout(
        clickmode="event",
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        template="plotly_white" if light_mode else "plotly_dark",
    )

    fig.update_layout(xaxis_range=[date_from, date_to])

    return fig


def generate_multi_ts_figure(
    data, date_from, date_to, light_mode=True, chart_type="line", layout_type="single"
):
    traces = []
    if chart_type == "line":
        for i in range(len(data)):
            traces.append(
                go.Scatter(
                    x=data[i][0],
                    y=data[i][1],
                    marker_color=MULTI_VIZ_COLORSCALE[i],
                    showlegend=False,
                    mode="lines",
                    hovertemplate="%{x}<br><b>%{y}</b><extra></extra>",
                )
            )
    elif chart_type == "scatter":
        for i in range(len(data)):
            traces.append(
                go.Scattergl(
                    x=data[i][0],
                    y=data[i][1],
                    marker_color=MULTI_VIZ_COLORSCALE[i],
                    showlegend=False,
                    mode="markers",
                    hovertemplate="%{x}<br><b>%{y}</b><extra></extra>",
                )
            )
    elif chart_type == "area":
        for i in range(len(data)):
            traces.append(
                go.Scattergl(
                    x=data[i][0],
                    y=data[i][1],
                    marker_color=MULTI_VIZ_COLORSCALE[i],
                    showlegend=False,
                    mode="lines",
                    fill="tozeroy",
                    hovertemplate="%{x}<br><b>%{y}</b><extra></extra>",
                )
            )
    elif chart_type == "bar":
        if len(data[0][0]) < 250:
            for i in range(len(data)):
                traces.append(
                    go.Bar(
                        x=data[i][0],
                        y=data[i][1],
                        marker_color=MULTI_VIZ_COLORSCALE[i],
                        showlegend=False,
                        hovertemplate="%{x}<br><b>%{y}</b><extra></extra>",
                    )
                )
        else:
            for i in range(len(data)):

                # create scattergl lines
                times_scatter = []
                values_scatter = []
                customdata = []
                for j in range(len(data[i][0])):
                    times_scatter.append(data[i][0][j])
                    times_scatter.append(data[i][0][j])
                    times_scatter.append(None)
                    values_scatter.append(0)
                    values_scatter.append(data[i][1][j])
                    values_scatter.append(None)
                    customdata.append(data[i][1][j])
                    customdata.append(data[i][1][j])
                    customdata.append("")
                traces.append(
                    go.Scattergl(
                        x=times_scatter,
                        y=values_scatter,
                        marker_color=MULTI_VIZ_COLORSCALE[i],
                        customdata=customdata,
                        mode="lines",
                        hovertemplate="%{x}<br><b>%{customdata}</b><extra></extra>",
                    )
                )

    if layout_type == "single":
        fig = go.Figure()

        for t in traces:
            fig.add_trace(t)
        fig.update_layout(xaxis_range=[date_from, date_to])

    elif layout_type == "subplots":
        traces_with_data = [t for t in traces if len(t.x) > 0]
        fig = make_subplots(
            rows=len(traces_with_data), cols=1, shared_xaxes=True, vertical_spacing=0.05
        )
        for i in range(len(traces_with_data)):

            fig.add_trace(trace=traces_with_data[i], row=i + 1, col=1)
            fig.update_xaxes(range=[date_from, date_to], row=i + 1, col=1)

    fig.update_layout(
        clickmode="event",
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        template="plotly_white" if light_mode else "plotly_dark",
        legend_orientation="h",
    )

    return fig


def generate_time_of_day_scatter(
    minutes_of_day,
    values,
    light_mode=True,
    marker_color=None,
    spike=False,
    chart_type="line",
):

    fig = go.Figure()
    fig.update_layout(
        margin=dict(l=30, r=30, t=20, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel_bgcolor="rgba(245, 245, 245,0.8)",
        hoverlabel_font_color="black",
        template="plotly_white" if light_mode else "plotly_dark",
    )
    if chart_type == "line":
        fig.add_trace(
            go.Scatter(
                x=minutes_of_day,
                y=values,
                mode="lines",
                line_shape="hv",
                line_width=1.5,
                marker_color=marker_color,
                customdata=[minute_to_tod(v) for v in minutes_of_day],
                hovertemplate="<b>%{customdata}</b>: %{y}<extra></extra>",
                showlegend=False,
            )
        )
    elif chart_type == "scatter":
        fig.add_trace(
            go.Scatter(
                x=minutes_of_day,
                y=values,
                mode="markers",
                marker_color=marker_color,
                customdata=[minute_to_tod(v) for v in minutes_of_day],
                hovertemplate="<b>%{customdata}</b>: %{y}<extra></extra>",
                showlegend=False,
            )
        )
    elif chart_type == "area":
        fig.add_trace(
            go.Scatter(
                x=minutes_of_day,
                y=values,
                mode="lines",
                line_shape="hv",
                fill="tozeroy",
                line_width=1.5,
                marker_color=marker_color,
                customdata=[minute_to_tod(v) for v in minutes_of_day],
                hovertemplate="<b>%{customdata}</b>: %{y}<extra></extra>",
                showlegend=False,
            )
        )
    elif chart_type == "bar":
        fig.add_trace(
            go.Bar(
                x=minutes_of_day,
                y=values,
                marker_color=marker_color,
                customdata=[minute_to_tod(v) for v in minutes_of_day],
                hovertemplate="<b>%{customdata}</b>: %{y}<extra></extra>",
                showlegend=False,
            )
        )

    if spike:
        fig.update_xaxes(
            showspikes=True,
            spikedash="solid",
            spikecolor="#96F2D7",
            spikemode="across",
            spikethickness=-2,
        )
        fig.update_layout(hovermode="x unified")
    fig.update_xaxes(ticktext=tod_ticklabels, tickvals=tod_tickvalues)
    fig.update_layout(xaxis_range=[0, 60 * 24])

    return fig


def generate_multi_time_of_day_scatter(
    data, light_mode=True, chart_type="line", layout_type="subplots"
):

    traces = []
    if chart_type == "line":
        for i in range(len(data)):
            traces.append(
                go.Scatter(
                    x=data[i][0],
                    y=data[i][1],
                    mode="lines",
                    line_shape="hv",
                    line_width=1.5,
                    marker_color=MULTI_VIZ_COLORSCALE[i],
                    customdata=[minute_to_tod(v) for v in data[i][0]],
                    hovertemplate="<b>%{customdata}</b>: %{y}<extra></extra>",
                    showlegend=False,
                )
            )
    elif chart_type == "scatter":
        for i in range(len(data)):
            traces.append(
                go.Scatter(
                    x=data[i][0],
                    y=data[i][1],
                    mode="markers",
                    marker_color=MULTI_VIZ_COLORSCALE[i],
                    customdata=[minute_to_tod(v) for v in data[i][0]],
                    hovertemplate="<b>%{customdata}</b>: %{y}<extra></extra>",
                    showlegend=False,
                )
            )
    elif chart_type == "area":
        for i in range(len(data)):
            traces.append(
                go.Scatter(
                    x=data[i][0],
                    y=data[i][1],
                    mode="lines",
                    line_shape="hv",
                    line_width=1.5,
                    marker_color=MULTI_VIZ_COLORSCALE[i],
                    customdata=[minute_to_tod(v) for v in data[i][0]],
                    hovertemplate="<b>%{customdata}</b>: %{y}<extra></extra>",
                    showlegend=False,
                    fill="tozeroy",
                )
            )
    elif chart_type == "bar":
        for i in range(len(data)):
            traces.append(
                go.Bar(
                    x=data[i][0],
                    y=data[i][1],
                    marker_color=MULTI_VIZ_COLORSCALE[i],
                    customdata=[minute_to_tod(v) for v in data[i][0]],
                    hovertemplate="<b>%{customdata}</b>: %{y}<extra></extra>",
                    showlegend=False,
                )
            )
    if layout_type == "single":
        fig = go.Figure()
        for trace in traces:
            fig.add_trace(trace)
    else:
        traces_with_data = [t for t in traces if len(t.x) > 0]
        fig = make_subplots(
            rows=len(traces_with_data), cols=1, shared_xaxes=True, vertical_spacing=0.05
        )
        for i in range(len(traces_with_data)):
            fig.add_trace(traces_with_data[i], row=i + 1, col=1)
    fig.update_layout(
        margin=dict(l=30, r=30, t=20, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel_bgcolor="rgba(245, 245, 245,0.8)",
        hoverlabel_font_color="black",
        template="plotly_white" if light_mode else "plotly_dark",
        modebar_orientation="v",
    )

    fig.update_xaxes(ticktext=tod_ticklabels, tickvals=tod_tickvalues)
    fig.update_layout(xaxis_range=[0, 60 * 24])

    return fig


def no_data_figure(light_mode=True, annotation="No Data"):
    fig = go.Figure()
    fig.update_layout(
        xaxis_visible=False,
        yaxis_visible=False,
        template="plotly_white" if light_mode else "plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    if annotation:
        fig.add_annotation(text=annotation, xref="paper", yref="paper", showarrow=False)
    return fig
