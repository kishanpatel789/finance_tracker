import plotly.graph_objects as go
from nicegui import ui

from ..theme import theme


def create() -> None:
    @ui.page("/")
    def home():
        with theme.frame():
            ui.label("Finance Tracker").classes("text-xl")
            ui.label("Placeholder for home dashboard")

            mint_green = "#78c2ad"
            mint_red = "#e25c5c"

            def make_bullet(fig, title, value, budget, y_domain):
                is_under = value <= budget
                delta_amount = round(abs(budget - value))
                delta_text = f"${delta_amount} {'left' if is_under else 'over'}"
                bar_color = mint_green if is_under else mint_red

                value_text = f"${value:,} of ${budget:,}"

                fig.add_trace(
                    go.Indicator(
                        mode="gauge",
                        value=value,
                        domain={"x": [0.1, 1], "y": y_domain},
                        title={
                            "text": f"<b>{title}</b><br><span style='color: gray; font-size:0.8em'>{delta_text}</span>",
                            "font": {"size": 14},
                        },
                        gauge={
                            "shape": "bullet",
                            "axis": {
                                "range": [None, max(value, budget)],
                                "visible": False,
                            },
                            "bar": {"color": bar_color, "thickness": 1},
                        },
                        customdata=[[value_text]],
                    )
                )

                # bar annotation - does not work
                y_center = (y_domain[0] + y_domain[1]) / 2
                x_pos = 0.12 + (value / max(value, budget))
                fig.add_annotation(
                    x=x_pos,
                    y=y_center,
                    text=value_text,
                    showarrow=False,
                    font=dict(color="white", size=12),
                    xanchor="left",
                    yanchor="middle",
                )

            fig = go.Figure()
            make_bullet(fig, "Groceries", value=150, budget=200, y_domain=[0.6, 0.8])
            make_bullet(fig, "Rent", value=2000.17, budget=1820, y_domain=[0.3, 0.5])

            fig.update_layout(
                height=300,
                margin=dict(t=30, b=30, l=30, r=30),
            )

            ui.plotly(fig)
