from nicegui import ui

from ..helpers import call_api, currency_str_to_float, format_currency
from ..theme import theme


def create() -> None:
    @ui.page("/categories/")
    def categories_page():
        with theme.frame():

            @ui.refreshable
            def categories_div():
                result = call_api("/categories/", method="GET")

                if result.data is None:
                    ui.label("No categories found").classes("text-gray-500")
                    return

                for row in result.data:
                    with ui.column().classes("space-y-1 w-full items-center"):
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

            def open_create_modal():
                with ui.dialog() as dialog, ui.card():
                    ui.label("Create Category").classes("text-lg font-semibold")

                    name = ui.input("Name").classes("w-full")
                    budget = ui.number("Budget").classes("w-full")

                    with ui.row():
                        ui.button("Cancel", on_click=dialog.close)
                        ui.button(
                            "Save",
                            on_click=lambda: submit_create(
                                dialog, name.value, budget.value
                            ),
                        )

                    dialog.open()

            def submit_create(dialog, name, budget):
                payload = {"name": name, "budget": budget}
                result = call_api("/categories/", payload=payload, method="POST")
                if result.success:
                    dialog.close()
                    categories_div.refresh()
                    ui.notify("Category created")

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
                result = call_api(f"/categories/{id}", payload=payload, method="PATCH")
                if result.success:
                    dialog.close()
                    categories_div.refresh()
                    ui.notify("Category updated")

            def delete_category(id):
                result = call_api(f"/categories/{id}", method="DELETE")
                if result.success:
                    categories_div.refresh()
                    ui.notify("Category deleted")

            # render content
            ui.label("Categories").classes("text-xl font-bold")
            ui.button("Add Category", on_click=lambda: open_create_modal())
            categories_div()
