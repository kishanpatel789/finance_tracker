from nicegui import ui

from ..helpers import call_api, format_currency
from ..theme import theme


def create() -> None:
    @ui.page("/categories/")
    def categories_page():
        with theme.frame():
            ui.label("Categories").classes("text-xl font-bold")

            container = ui.column().classes("space-y-1 w-full items-center")

            def refresh():
                container.clear()
                data = call_api("/categories/", method="GET")

                for row in data:
                    with container:
                        with ui.row().classes(
                            "w-96 justify-between items-center bg-white rounded-lg shadow-sm p-4"
                        ):
                            with ui.column():
                                ui.label(row["name"]).classes("text-md font-medium")
                                ui.label(format_currency(row["budget"])).classes(
                                    "text-gray-600"
                                )
                            with ui.row().classes("gap-2"):
                                ui.button("Edit").classes(
                                    "px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                                )
                                ui.button("Delete").classes(
                                    "px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                                )

            ui.button("Add Category", on_click=lambda: ui.notify("TODO: Add category"))

            refresh()
