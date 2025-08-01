import plotly.graph_objects as go
from nicegui import ui

from ..theme import theme


def create() -> None:
    @ui.page("/")
    def home():
        with theme.frame():
            ui.label("Finance Tracker").classes("text-xl")
            ui.label("Placeholder for home dashboard")

            fig = go.Figure(
                go.Indicator(
                    mode="number+gauge+delta",
                    gauge={"shape": "bullet"},
                    value=150,
                    delta={"reference": 200},
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Groceries"},
                )
            )
            fig.update_layout(height=250)
            ui.plotly(fig)

            fig = go.Figure(
                go.Indicator(
                    mode="number+gauge+delta",
                    gauge={"shape": "bullet"},
                    value=2000,
                    delta={"reference": 1820},
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Rent"},
                )
            )
            fig.update_layout(height=250)
            ui.plotly(fig)
