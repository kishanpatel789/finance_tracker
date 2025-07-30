from contextlib import contextmanager

from nicegui import ui


@contextmanager
def frame():
    """Custom page frame to share the same styling and behavior across all pages"""
    with ui.header().classes("items-center justify-between"):
        ui.label("Finance Tracker").classes("font-bold text-3xl")

        with ui.button(icon="menu"):
            with ui.menu():
                ui.menu_item("Home", lambda: ui.navigate.to("/"))
                ui.menu_item("Transactions", lambda: ui.navigate.to("/transactions/"))
                ui.menu_item("Categories", lambda: ui.navigate.to("/categories/"))

    # page content goes here
    with ui.column().classes("w-full items-center"):
        yield
