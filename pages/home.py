import streamlit as st


class Home:
    def __init__(self, aequitas):
        self.aequitas = aequitas

    def run(self):
        st.write("Welcome to the Home page")
        # upload csv file
        uploaded_file = st.file_uploader("Update spendings", type="xls")
        if uploaded_file is not None:
            st.write("File uploaded")
            # update the table
            self.aequitas.update_table(uploaded_file)
            st.write(f"Table {self.aequitas.table.table_name} updated")
            st.write(self.aequitas.get_data().head(5))
