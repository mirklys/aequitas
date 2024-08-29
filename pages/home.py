import streamlit as st
import plotly.express as px

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

        # amount between dates
        st.write("Select a date range")
        start_date = st.date_input("Start date")
        end_date = st.date_input("End date")

        if start_date is None:
            start_date = self.aequitas.get_data()["date"].min()
        if end_date is None:
            end_date = self.aequitas.get_data()["date"].max()

        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
        if start_date > end_date:
            st.warning("Start date should be before end date")
            

        incoming = incoming.loc[(incoming["date"] >= start_date) & (incoming["date"] <= end_date)]
        outgoing = outgoing.loc[(outgoing["date"] >= start_date) & (outgoing["date"] <= end_date)]

        st.write(f"Total incoming between {start_date} and {end_date}: {incoming['amount'].sum().round(2)} EUR")
        st.write(f"Total outgoing between {start_date} and {end_date}: {outgoing['amount'].sum().round(2)} EUR")
        st.write(f"Total balance between {start_date} and {end_date}: {(incoming['amount'].sum() - outgoing['amount'].sum()).round(2)} EUR")

        # Count the number of transactions per category
        # Count the number of transactions per category

        category_counts = outgoing['category'].value_counts()

        # Create a pie chart using Plotly
        fig = px.pie(values=category_counts, names=category_counts.index, title='Spending Categories Pie Chart')

        # Streamlit components
        st.title('Spending Categories Pie Chart')
        st.plotly_chart(fig)

        # get the sum of the amount per category
        category_sum = outgoing.groupby("category")["amount"].sum()
        fig = px.bar(x=category_sum.index, y=category_sum.values, title="Spending Categories Bar Chart")
        st.title("Spending Categories Bar Chart")
        st.plotly_chart(fig)
        




        
