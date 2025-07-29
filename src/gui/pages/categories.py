from nicegui import ui

from ..helpers import call_api, currency_str_to_float, format_currency
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
                                ui.button(
                                    icon="edit",
                                    on_click=lambda r=row: open_edit_modal(r),
                                ).props("color=primary dense")
                                ui.button(
                                    icon="delete",
                                    on_click=lambda r=row: delete_category(r["id"]),
                                ).props("color=negative dense")

            ui.button("Add Category", on_click=lambda: ui.notify("TODO: Add category"))

            def open_edit_modal(row):
                with ui.dialog() as dialog, ui.card():
                    ui.label("Edit Category").classes("text-lg font-semibold")

                    name = ui.input("Name", value=row["name"]).classes("w-full")
                    budget = ui.number(
                        "Budget", value=currency_str_to_float(row["budget"])
                    ).classes("w-full")

                    with ui.row():
                        ui.button("Cancel", on_click=dialog.close)
                        ui.button(
                            "Save",
                            on_click=lambda: submit_edit(
                                dialog, row["id"], name.value, budget.value
                            ),
                        )

                    dialog.open()

            def submit_edit(dialog, id, name, budget):
                payload = {"name": name, "budget": budget}
                call_api(f"/categories/{id}", payload=payload, method="PATCH")
                dialog.close()
                refresh()
                ui.notify("Category updated")

            def delete_category(id):
                call_api(f"/categories/{id}", method="DELETE")
                refresh()
                ui.notify("Category deleted")

            refresh()
