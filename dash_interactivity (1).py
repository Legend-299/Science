import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# compute min/max payload for the slider
min_payload = spacex_df["Payload Mass (kg)"].min()
max_payload = spacex_df["Payload Mass (kg)"].max()

# ─── INSTANTIATE APP ──────────────────────────────────────────────────────────
app = Dash(__name__)

# ─── LAYOUT ───────────────────────────────────────────────────────────────────
app.layout = html.Div(
    style={"width": "100%", "padding": "10px"},
    children=[

        # 1) Centered page title
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "marginBottom": "20px"}
        ),

        # 2) Full-width dropdown
        dcc.Dropdown(
            id="site-dropdown",
            options=[
                {"label": "All Sites",    "value": "ALL"},
                {"label": "CCAFS LC-40",  "value": "CCAFS LC-40"},
                {"label": "VAFB SLC-4E",  "value": "VAFB SLC-4E"},
                {"label": "KSC LC-39A",   "value": "KSC LC-39A"},
                {"label": "CCAFS SLC-40", "value": "CCAFS SLC-40"},
            ],
            value="ALL",
            placeholder="All Sites",
            style={"width": "100%", "fontSize": "16px"}
        ),

        html.Br(),

        # 3) Pie Chart with mode-bar icons
        dcc.Graph(
            id="success-pie-chart",
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "modeBarButtons": [
                    ["toImage", "resetScale2d", "toggleSpikelines"]
                ]
            }
        ),

        html.Br(),

        # 4) Payload RangeSlider
        html.P("Payload range (Kg):", style={"marginLeft": "5px"}),
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
            value=[min_payload, max_payload],
            tooltip={"placement": "bottom"},
            updatemode='mouseup',
            allowCross=False
        ),

        html.Br(),

        # 5) Scatter plot placeholder with same mode-bar icons
        dcc.Graph(
            id="success-payload-scatter-chart",
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "modeBarButtons": [
                    ["toImage", "resetScale2d", "toggleSpikelines"]
                ]
            }
        ),
    ]
)

# ─── CALLBACK TO RENDER PIE CHART ──────────────────────────────────────────────
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value")
)
def update_pie_chart(entered_site):
    if entered_site == "ALL":
        df = spacex_df.groupby("Launch Site")["class"].sum().reset_index()
        fig = px.pie(df,
                     names="Launch Site",
                     values="class",
                     title="Total Success Launches By Site")
    else:
        dff = spacex_df[spacex_df["Launch Site"] == entered_site]
        counts = dff["class"].value_counts().reset_index()
        counts.columns = ["class", "count"]
        fig = px.pie(counts,
                     names="class",
                     values="count",
                     title=f"Total Success Launches for site {entered_site}")

    fig.update_layout(title_x=0.5)
    return fig

# ─── TASK 4 CALLBACK: SCATTER PLOT ─────────────────────────────────────────────
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [
        Input("site-dropdown", "value"),
        Input("payload-slider", "value")
    ]
)
def update_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # filter by payload range
    df_filtered = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low) &
        (spacex_df["Payload Mass (kg)"] <= high)
    ]

    # if a site is selected, filter by that too
    if entered_site != "ALL":
        df_filtered = df_filtered[df_filtered["Launch Site"] == entered_site]

    # build the scatter
    fig = px.scatter(df_filtered,
                     x="Payload Mass (kg)",
                     y="class",
                     color="Booster Version Category",
                     title=("Correlation between Payload and Success "
                            + (f"for site {entered_site}"
                               if entered_site != "ALL" else "for all Sites"))
                     )

    fig.update_layout(title_x=0.5,
                      xaxis_title="Payload Mass (kg)",
                      yaxis_title="Class")
    return fig

# ─── RUN THE APP ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run()