from nicegui import ui

from ..helpers import (
    call_api,
    currency_str_to_float,
    format_currency,
    get_selectable_categories,
)
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
                                    on_click=lambda r=row: open_edit_modal(r),
                                ).props("color=primary dense")
                                ui.button(
                                    icon="delete",
                                    on_click=lambda r=row: delete_transaction(r["id"]),
                                ).props("color=negative dense")

            def open_edit_modal(row):
                with ui.dialog() as dialog, ui.card():
                    ui.label("Edit Transaction").classes("text-lg font-semibold")

                    with ui.row():
                        with ui.column():
                            with ui.input("Date", value=row["trans_date"]) as date:
                                with ui.menu().props("no-parent-event") as menu:
                                    with ui.date().bind_value(date):
                                        with ui.row().classes("justify-end"):
                                            ui.button(
                                                "Close", on_click=menu.close
                                            ).props("flat")
                                with date.add_slot("append"):
                                    ui.icon("edit_calendar").on(
                                        "click", menu.open
                                    ).classes("cursor-pointer")

                            vendor = ui.input("Vendor", value=row["vendor"]).classes(
                                "w-full"
                            )
                            amount = ui.number(
                                "Amount", value=currency_str_to_float(row["amount"])
                            ).classes("w-full")
                        with ui.column():
                            note = ui.textarea("Note", value=row["note"]).classes(
                                "w-full"
                            )
                            current_category_id = (
                                row["category"]["id"] if row["category"] else None
                            )
                            category_id = ui.select(
                                options=get_selectable_categories(),
                                value=current_category_id,
                                with_input=True,
                            ).classes("w-40")

                    with ui.row():
                        ui.button("Cancel", on_click=dialog.close)
                        ui.button(
                            "Save",
                            on_click=lambda: submit_edit(
                                dialog,
                                row["id"],
                                vendor=vendor.value,
                                trans_date=date.value,
                                note=note.value,
                                amount=amount.value,
                                category_id=category_id.value,
                            ),
                        )

                    dialog.open()

            def submit_edit(dialog, id, **payload):
                if "category_id" in payload and payload["category_id"] == "__NONE__":
                    payload["category_id"] = None
                call_api(f"/transactions/{id}", payload=payload, method="PATCH")
                dialog.close()
                transactions_div.refresh()
                ui.notify("Transaction updated")

            def delete_transaction(id):
                call_api(f"/transactions/{id}", method="DELETE")
                transactions_div.refresh()
                ui.notify("Transaction deleted")

            # render content
            ui.label("Transactions").classes("text-xl font-bold")
            ui.button("Add Transaction")
            transactions_div()
