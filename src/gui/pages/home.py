from datetime import date

import plotly.graph_objects as go
from nicegui import ui

from ..helpers import call_api, currency_str_to_float, get_month_options
from ..theme import theme


def create() -> None:
    @ui.page("/")
    def home():
        with theme.frame():
            mint_green = "#78c2ad"
            mint_red = "#e25c5c"

            def make_bullet(
                fig: go.Figure,
                title: str,
                value_str: str,
                budget_str: str,
                y_domain: list[float],
            ):
                value = currency_str_to_float(value_str)
                budget = currency_str_to_float(budget_str)
                is_under = value <= budget
                bar_color = mint_green if is_under else mint_red

                if budget_str is not None:
                    delta_amount = round(abs(budget - value))
                    delta_text = f"${delta_amount:,} {'left' if is_under else 'over'}"
                else:
                    delta_text = ""

                if title is None:
                    title = "No Category"

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
                                "range": [
                                    0.0,
                                    max(value, budget, 1),
                                ],  # max must be at least 1 for proper rendering
                                "visible": False,
                            },
                            "bar": {"color": bar_color, "thickness": 1},
                        },
                        number={
                            "font": {
                                "size": 16,
                            },
                            "prefix": "$",
                            "valueformat": ",.2f",
                        },
                    )
                )

            def search_div():
                options = get_month_options(13)
                ui.select(
                    options,
                    value=next(iter(options.keys())),
                    on_change=lambda e: report_div.refresh(e.value),
                )

            @ui.refreshable
            def report_div(year_month: str):
                fig = go.Figure()

                result = call_api(
                    f"reports/monthly_budget?year_month={year_month}", method="GET"
                )
                num_lines = len(result.data)
                spacing = 0.01
                for i, line in enumerate(result.data):
                    make_bullet(
                        fig,
                        line["category_name"],
                        value_str=line["amount_spent"],
                        budget_str=line["budget"],
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

            # set initial state
            initial_year_month: str = date.today().strftime("%Y-%m")

            # render content
            ui.label("Finance Tracker").classes("text-xl")
            search_div()
            report_div(initial_year_month)
