from nicegui import ui

from .pages import categories, home

home.create()
categories.create()


ui.run(title="Finance Tracker")
