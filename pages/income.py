import streamlit as st


class Income:
    def __init__(self, aequitas):
        self.aequitas = aequitas

    def run(self):
        st.write("Total Income: $", self.income)
