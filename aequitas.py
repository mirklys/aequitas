import streamlit as st
import os
import importlib
from scripts.database import Database

# Title of the dashboard
st.title("AEQUITAS")


class Aequitas:
    def __init__(self, db_name):
        self.db = Database(db_name)
        self.table = self.db.add_table("transactions")
        self.pages = self.retrieve_pages()

    def retrieve_pages(self):
        folder = "pages"

        # retrieve all the pages in the folder and their classes, one main class per page
        pages = {}
        for filename in os.listdir(folder):
            if filename.endswith(".py") and filename != "__init__.py":
                page_name = filename[:-3]  # Remove the ".py" extension
                page_path = f"{folder}.{page_name}"
                page = importlib.import_module(page_path)
                class_name = page_name.capitalize()
                page_class = getattr(page, class_name)
                pages[class_name] = page_class

        return pages

    def update_table(self, xsl_file):
        old_size = self.table.size
        self.table.update_table_from_xsl(xsl_file)
        self.table = self.db.get_table("transactions")
        new_size = self.table.size
        st.write(
            f"Table {self.table.table_name} updated from {old_size} to {new_size} rows"
        )

    def get_data(self):
        return self.table.get_data_from_table()

    def process_data(self):
        data = self.get_data()
        return data

    def run(self, itself):
        st.sidebar.title("Navigation")
        selection = st.sidebar.radio("Go to", list(self.pages.keys()))
        page = self.pages[selection](itself)
        page.run()


if __name__ == "__main__":
    aequitas = Aequitas("data/database/aequitas.db")
    aequitas.run(aequitas)
