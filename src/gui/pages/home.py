import plotly.graph_objects as go
from nicegui import ui

from ..helpers import call_api, currency_str_to_float
from ..theme import theme


def create() -> None:
    @ui.page("/")
    def home():
        with theme.frame():
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
                        mode="gauge+number",
                        value=value,
                        domain={"x": [0.2, 1], "y": y_domain},
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
                        number={
                            "font": {
                                "size": 20,
                            },
                            "prefix": "$",
                            "valueformat": ",.2f",
                        },
                        customdata=[[value_text]],
                    )
                )

            @ui.refreshable
            def report_div():
                fig = go.Figure()

                result = call_api(
                    "reports/monthly_budget?year_month=2025-07", method="GET"
                )
                num_lines = len(result.data)
                spacing = 0.01
                for i, line in enumerate(result.data):
                    make_bullet(
                        fig,
                        line["category_name"],
                        value=currency_str_to_float(line["amount_spent"]),
                        budget=currency_str_to_float(line["budget"]),
                        y_domain=[
                            (num_lines - i - 1) / num_lines + spacing,
                            (num_lines - i) / num_lines - spacing,
                        ],
                    )

                fig.update_layout(
                    height=60 * num_lines,
                    margin=dict(t=30, b=30, l=30, r=30),
                )
                ui.plotly(fig)

            # render content
            ui.label("Finance Tracker").classes("text-xl")
            ui.label("Placeholder for home dashboard")
            report_div()
