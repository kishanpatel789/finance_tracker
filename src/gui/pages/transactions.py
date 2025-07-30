from nicegui import ui

from ..helpers import call_api, format_currency
from ..theme import theme


def create() -> None:
    @ui.page("/transactions/")
    def transactions_page():
        with theme.frame():

            @ui.refreshable
            def transactions_div():
                response = call_api("/transactions/", method="GET")

                grid_classes = (
                    "grid grid-cols-6 gap-4 w-full justify-between items-center px-4"
                )

                with ui.column().classes("space-y-1 w-full items-center"):
                    # header row
                    with ui.row().classes(f"{grid_classes} font-bold"):
                        ui.label("Date").classes("col-span-1")
                        ui.label("Vendor").classes("col-span-1")
                        ui.label("Category").classes("col-span-1")
                        ui.label("Note").classes("col-span-1")
                        ui.label("Amount").classes("col-span-1 text-right mr-2")

                    # data rows
                    for row in response["data"]:
                        with ui.row().classes(
                            f"{grid_classes} bg-white rounded-lg shadow-sm"
                        ):
                            ui.label(row["trans_date"]).classes("col-span-1")
                            ui.label(row["vendor"]).classes("col-span-1")
                            if row["category"] is not None:
                                ui.label(row["category"]["name"]).classes("col-span-1")
                            else:
                                ui.label("").classes("col-span-1")
                            ui.label(row["note"]).classes("col-span-1")
                            ui.label(format_currency(row["amount"])).classes(
                                "col-span-1 text-right mr-2"
                            )
                            with ui.row().classes("gap-2 col-span-1 justify-end"):
                                ui.button(
                                    icon="edit",
                                    #                                    on_click=lambda r=row: open_edit_modal(r),
                                ).props("color=primary dense")
                                ui.button(
                                    icon="delete",
                                    on_click=lambda r=row: delete_transaction(r["id"]),
                                ).props("color=negative dense")

            def delete_transaction(id):
                call_api(f"/transactions/{id}", method="DELETE")
                transactions_div.refresh()
                ui.notify("Transaction deleted")

            # render content
            ui.label("Transactions").classes("text-xl font-bold")
            ui.button("Add Transaction")
            transactions_div()
