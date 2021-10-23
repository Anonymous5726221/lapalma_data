import plotly.io as pio
from copy import deepcopy


lpmtg_template = pio.templates["plotly_dark"]

lpmtg_template.layout.annotations = [
    dict(
        name="LPMTG watermark",
        text="/LPMTG/",
        textangle=-30,
        opacity=0.1,
        font=dict(color="white", size=100),
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
    )
]

plot_color = "#222222" # Same color as page background to make plot appear transparent

lpmtg_template.layout.paper_bgcolor = plot_color
lpmtg_template.layout.plot_bgcolor = plot_color
