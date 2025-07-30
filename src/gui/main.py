from nicegui import ui

from .pages import categories, home, transactions

home.create()
categories.create()
transactions.create()


ui.run(title="Finance Tracker")
