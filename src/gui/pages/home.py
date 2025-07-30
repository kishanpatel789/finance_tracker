from nicegui import ui

from ..theme import theme


def create() -> None:
    @ui.page("/")
    def home():
        with theme.frame():
            ui.label("Finance Tracker").classes("text-xl")
            ui.label("Placeholder for home dashboard")
