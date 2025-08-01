import datetime

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

            def search_div(initial_start_date: str = "", initial_end_date: str = ""):
                with ui.row().classes("items-center"):
                    search_query = ui.input(label="Search Term").on(
                        "keydown.enter",
                        lambda: submit_search(
                            q=search_query.value,
                            start_date=start_date.value,
                            end_date=end_date.value,
                        ),
                    )

                    with ui.input("From Date", value=initial_start_date) as start_date:
                        with ui.menu().props("no-parent-event") as menu:
                            with ui.date().bind_value(start_date):
                                with ui.row().classes("justify-end"):
                                    ui.button("Close", on_click=menu.close).props(
                                        "flat"
                                    )
                        with start_date.add_slot("append"):
                            ui.icon("edit_calendar").on("click", menu.open).classes(
                                "cursor-pointer"
                            )

                    with ui.input("To Date", value=initial_end_date) as end_date:
                        with ui.menu().props("no-parent-event") as menu:
                            with ui.date().bind_value(end_date):
                                with ui.row().classes("justify-end"):
                                    ui.button("Close", on_click=menu.close).props(
                                        "flat"
                                    )
                        with end_date.add_slot("append"):
                            ui.icon("edit_calendar").on("click", menu.open).classes(
                                "cursor-pointer"
                            )

                    ui.button(
                        "Search",
                        on_click=lambda: submit_search(
                            q=search_query.value,
                            start_date=start_date.value,
                            end_date=end_date.value,
                        ),
                    )

            def submit_search(**kwargs):
                params = {key: value for key, value in kwargs.items() if value != ""}
                params["page"] = 1  # reset to first page on search

                transactions_div.refresh(params=params)

            @ui.refreshable
            def transactions_div(*, params: dict | None = None):
                if params is None:
                    params = {}
                result = call_api("/transactions/", payload=params, method="GET")

                if not result.success:
                    ui.label("No transactions found").classes("text-gray-500")
                    return

                # pagination controls
                total_page_count = result.data["total_page_count"]
                with ui.row():
                    ui.pagination(
                        min=1,
                        max=total_page_count,
                        value=params.get("page", 1),
                        direction_links=True,
                        on_change=lambda page: update_page(page.value, params),
                    )

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
                    for row in result.data["data"]:
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

            def open_create_modal():
                with ui.dialog() as dialog, ui.card().classes("w-[700px]"):
                    ui.label("Add Transaction").classes("text-lg font-semibold")

                    with ui.row().classes("gap-4"):
                        # date selector
                        with ui.input(
                            "Date", value=datetime.date.today().isoformat()
                        ) as date:
                            with ui.menu().props("no-parent-event") as menu:
                                with ui.date().bind_value(date):
                                    with ui.row().classes("justify-end"):
                                        ui.button("Close", on_click=menu.close).props(
                                            "flat"
                                        )
                            with date.add_slot("append"):
                                ui.icon("edit_calendar").on("click", menu.open).classes(
                                    "cursor-pointer"
                                )

                        amount = ui.number("Amount").classes("w-full")
                    with ui.row().classes("gap-4"):
                        vendor = ui.input("Vendor").classes("w-full")
                        # category drop-down selector
                        category_id = ui.select(
                            label="Category",
                            options=get_selectable_categories(),
                            with_input=True,
                        ).classes("w-full")
                    with ui.row():
                        note = ui.textarea("Note").classes("w-full")

                    with ui.row():
                        ui.button("Cancel", on_click=dialog.close)
                        ui.button(
                            "Save",
                            on_click=lambda: submit_create(
                                dialog,
                                vendor=vendor.value,
                                trans_date=date.value,
                                note=note.value,
                                amount=amount.value,
                                category_id=category_id.value,
                            ),
                        )

                    dialog.open()

            def submit_create(dialog, **payload):
                if "category_id" in payload and payload["category_id"] == "__NONE__":
                    payload["category_id"] = None
                result = call_api("/transactions/", payload=payload, method="POST")
                if result.success:
                    dialog.close()
                    transactions_div.refresh()
                    ui.notify("Transaction created")

            def open_edit_modal(row):
                with ui.dialog() as dialog, ui.card().classes("w-[700px]"):
                    ui.label("Edit Transaction").classes("text-lg font-semibold")

                    with ui.row().classes("gap-4"):
                        # date selector
                        with ui.input("Date", value=row["trans_date"]) as date:
                            with ui.menu().props("no-parent-event") as menu:
                                with ui.date().bind_value(date):
                                    with ui.row().classes("justify-end"):
                                        ui.button("Close", on_click=menu.close).props(
                                            "flat"
                                        )
                            with date.add_slot("append"):
                                ui.icon("edit_calendar").on("click", menu.open).classes(
                                    "cursor-pointer"
                                )

                        amount = ui.number(
                            "Amount", value=currency_str_to_float(row["amount"])
                        ).classes("w-full")
                    with ui.row().classes("gap-4"):
                        vendor = ui.input("Vendor", value=row["vendor"]).classes(
                            "w-full"
                        )
                        # category drop-down selector
                        current_category_id = (
                            row["category"]["id"] if row["category"] else None
                        )
                        category_id = ui.select(
                            options=get_selectable_categories(),
                            label="Category",
                            value=current_category_id,
                            with_input=True,
                        ).classes("w-full")
                    with ui.row():
                        note = ui.textarea("Note", value=row["note"]).classes("w-full")

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
                result = call_api(
                    f"/transactions/{id}", payload=payload, method="PATCH"
                )
                if result.success:
                    dialog.close()
                    transactions_div.refresh()
                    ui.notify("Transaction updated")

            def delete_transaction(id):
                result = call_api(f"/transactions/{id}", method="DELETE")
                if result.success:
                    transactions_div.refresh()
                    ui.notify("Transaction deleted")

            def update_page(page, params):
                params["page"] = page
                transactions_div.refresh(params=params)

            # set initial state
            initial_start_date: str = (
                datetime.date.today() - datetime.timedelta(days=60)
            ).isoformat()
            initial_end_date: str = datetime.date.today().isoformat()
            params: dict[str, str] = {
                "start_date": initial_start_date,
                "end_date": initial_end_date,
            }

            # render content
            ui.label("Transactions").classes("text-xl font-bold")
            ui.button("Add Transaction", on_click=open_create_modal)
            search_div(initial_start_date, initial_end_date)
            transactions_div(params=params)
