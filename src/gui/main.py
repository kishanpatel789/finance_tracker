from nicegui import ui

API_BASE = "http://localhost:8000"


@ui.page("/")
def home():
    ui.label("Finance Tracker").classes("text-xl")


@ui.page("/categories")
def categories_page():
    ui.label("Categories").classes("text-xl font-bold")

    with ui.column().classes("gap-2"):
        ui.table(
            columns=[
                {"name": "id", "label": "ID"},
                {"name": "name", "label": "Name"},
                {"name": "budget", "label": "Budget"},
            ],
            rows=[],
            row_key="id",
        ).classes("w-full")

        ui.button("Add Category", on_click=lambda: ui.notify("TODO: Add category"))


ui.run(title="Finance Tracker")
