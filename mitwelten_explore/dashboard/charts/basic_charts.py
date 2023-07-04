import plotly.graph_objects as go
import plotly.express as px


def pie_chart(labels, values, light_mode=True, hole=0.3):
    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            textposition="inside",
            showlegend=False,
            hole=hole,
            textinfo="label+percent",
        )
    )
    fig.update_layout(
        template="plotly_white" if light_mode else "plotly_dark",
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        # colorway = px.colors.colorbrewer.Set1,
        colorway=px.colors.colorbrewer.Dark2,
        uniformtext_mode="hide",
        uniformtext_minsize=10,
    )
    return fig


def spider_chart(labels, keys, entries, light_mode=True, maxdist=1000):
    fig = go.Figure()
    opacities = [1.0, 0.8, 0.7, 0.7]
    colors = ["#A61E4D", "#D6336C", "#F06595", "#FAA2C1"]

    fig.add_trace(
        go.Scatterpolar(
            r=[10 for i in range(len(keys) + 1)],
            theta=labels + [labels[0]],
            mode="lines",
            line_width=3,
            line_color="grey",
            opacity=0.5,
            hoverinfo="skip",
            showlegend=False,
        )
    )
    for i in range(len(entries)):
        distance_m = int(entries[i].get("distance"))
        id = entries[i].get("environment_id")
        values = [entries[i][k] for k in keys]
        values = [v if v >= 0 else None for v in values]
        fig.add_trace(
            go.Scatterpolar(
                r=values + [values[0]],
                theta=labels + [labels[0]],
                fill="toself" if i == 0 else None,
                name=f"ID {id} ({distance_m} m)",
                mode="lines+markers",
                line_width=3 if i == 0 else 2,
                line_color=colors[i],
                opacity=opacities[i],
                hovertemplate="%{theta}: <b>%{r}</b> / 10",
            )
        )
    fig.update_layout(
        template="plotly_white" if light_mode else "plotly_dark",
        polar=dict(
            radialaxis=dict(
                # gridcolor="grey"
            ),
            angularaxis=dict(
                gridcolor="white",
                # rotation=1.3
            ),
            gridshape="linear",
            bgcolor="rgba(0,0,0,0)",
        ),
        margin_pad=90,
        font_size=11,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h"),
    )

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
