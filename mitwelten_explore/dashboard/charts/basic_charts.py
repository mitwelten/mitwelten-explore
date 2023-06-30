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
