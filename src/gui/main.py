from nicegui import ui

from .helpers import call_api


@ui.page("/")
def home():
    ui.label("Finance Tracker").classes("text-xl")


@ui.page("/categories/")
def categories_page():
    data = call_api("/categories/", method="GET")

    ui.label("Categories").classes("text-xl font-bold")

    with ui.column().classes("gap-2"):
        ui.table(
            columns=[
                {
                    "name": "id",
                    "label": "ID",
                    "field": "id",
                },
                {
                    "name": "name",
                    "label": "Name",
                    "field": "name",
                },
                {
                    "name": "budget",
                    "label": "Budget",
                    "field": "budget",
                },
            ],
            rows=data,
            row_key="id",
        ).classes("w-full")

        ui.button("Add Category", on_click=lambda: ui.notify("TODO: Add category"))


ui.run(title="Finance Tracker")
