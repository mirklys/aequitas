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
        
        # amount of incoming money and outgoing money
        incoming = self.aequitas.get_data().loc[self.aequitas.get_data()["incoming"] == 1]
        outgoing = self.aequitas.get_data().loc[self.aequitas.get_data()["incoming"] == 0]

        st.write(f"Total incoming: {incoming['amount'].sum().round(2)} EUR")
        st.write(f"Total outgoing: {outgoing['amount'].sum().round(2)} EUR")
        st.write(f"Total balance: {(incoming['amount'].sum() - outgoing['amount'].sum()).round(2)} EUR")

        
