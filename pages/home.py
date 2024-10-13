import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

class Home:
    def __init__(self, aequitas):
        self.aequitas = aequitas

    def run(self):
        # Title and Header
        st.title("💰 Personal Finance Dashboard")
        st.markdown("Analyze your income, expenses, and spending categories with insights and trends.")

        # Top-level metrics display
        st.markdown("### Monthly Overview")
        
        # Adjust column width by creating more columns with specific ratios
        col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 1.5])  # Increase width of each column

        # Get current and last month
        this_month = datetime.now().month
        last_month = this_month - 1
        if last_month == 0:
            last_month = 12

        data = self.aequitas.get_data()
        data["date"] = pd.to_datetime(data["date"])

        # Format numbers to fit better (reduce to two decimals and compact)
        this_month_income_value = round(data.loc[(data['incoming'] == 1) & (data['date'].dt.month == this_month)]['amount'].sum(), 2)
        this_month_expenses_value = round(data.loc[(data['incoming'] == 0) & (data['date'].dt.month == this_month)]['amount'].sum(), 2)
        last_month_income_value = round(data.loc[(data['incoming'] == 1) & (data['date'].dt.month == last_month)]['amount'].sum(), 2)
        last_month_expenses_value = round(data.loc[(data['incoming'] == 0) & (data['date'].dt.month == last_month)]['amount'].sum(), 2)

        # Display metrics with shortened values
        col1.metric(label="📈 This Month Income", value=f"{this_month_income_value:,} EUR")
        col2.metric(label="📉 This Month Expenses", value=f"{this_month_expenses_value:,} EUR")
        col3.metric(label="🗓️ Last Month Income", value=f"{last_month_income_value:,} EUR")
        col4.metric(label="🗓️ Last Month Expenses", value=f"{last_month_expenses_value:,} EUR")

        # Upload new spending data
        st.markdown("### Upload Spending Data")
        uploaded_file = st.file_uploader("Update spendings", type="xls")
        if uploaded_file is not None:
            st.write("File uploaded")
            # update the table
            self.aequitas.update_table(uploaded_file)
            st.write(f"Table {self.aequitas.table.table_name} updated")
            st.write(data.head(5))

        # Total income and expenses overview
        incoming = data.loc[data['incoming'] == 1]
        outgoing = data.loc[data['incoming'] == 0]
        total_incoming = incoming['amount'].sum().round(2)
        total_outgoing = outgoing['amount'].sum().round(2)
        balance = (total_incoming - total_outgoing).round(2)

        st.markdown("### Total Financial Overview")
        st.write(f"💵 **Total Incoming**: {total_incoming} EUR")
        st.write(f"💸 **Total Outgoing**: {total_outgoing} EUR")
        st.write(f"💰 **Net Balance**: {balance} EUR")

        # Date Range Filter
        st.markdown("### Analyze Income and Expenses Over a Time Range")
        start_date = st.date_input("Start date")
        end_date = st.date_input("End date")
        if start_date and end_date:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            if start_date > end_date:
                st.warning("Start date should be before the end date")
            else:
                filtered_incoming = incoming.loc[(incoming['date'] >= start_date) & (incoming['date'] <= end_date)]
                filtered_outgoing = outgoing.loc[(outgoing['date'] >= start_date) & (outgoing['date'] <= end_date)]

                st.write(f"📈 **Total incoming** between {start_date.date()} and {end_date.date()}: {filtered_incoming['amount'].sum().round(2)} EUR")
                st.write(f"📉 **Total outgoing** between {start_date.date()} and {end_date.date()}: {filtered_outgoing['amount'].sum().round(2)} EUR")
                st.write(f"💰 **Net balance**: {(filtered_incoming['amount'].sum() - filtered_outgoing['amount'].sum()).round(2)} EUR")

        # Spending categories - Pie chart
        st.markdown("### Spending Categories Breakdown")
        category_counts = outgoing['category'].value_counts()
        fig_pie = px.pie(values=category_counts, names=category_counts.index, title="Spending by Category")
        st.plotly_chart(fig_pie)

        # Sum per category - Bar chart
        category_sum = outgoing.groupby('category')['amount'].sum()
        fig_bar = px.bar(x=category_sum.index, y=category_sum.values, title="Total Spending per Category", labels={'x': 'Category', 'y': 'Total Amount'})
        st.plotly_chart(fig_bar)

        # Spending trend over time - Curved Line Graph
        st.markdown("### Spending Trends Over Time")
        outgoing_time_series = outgoing.groupby(outgoing['date'].dt.to_period('M')).agg({'amount': 'sum'})
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=outgoing_time_series.index.astype(str), 
                                      y=outgoing_time_series['amount'], 
                                      mode='lines+markers', 
                                      line_shape='spline',  # Smooth curved lines
                                      name='Spending Over Time'))
        fig_line.update_layout(title='Monthly Spending Trend', xaxis_title='Month', yaxis_title='Total Spending (EUR)')
        st.plotly_chart(fig_line)

        # Top Vendors (by amount spent)
        st.markdown("### Top Vendors by Spending")
        vendor_sum = outgoing.groupby('name')['amount'].sum().nlargest(5)
        fig_top_vendors = px.bar(x=vendor_sum.index, y=vendor_sum.values, title="Top 5 Vendors by Spending", labels={'x': 'Vendor', 'y': 'Total Amount'})
        st.plotly_chart(fig_top_vendors)

        # Footer/Conclusion
        st.markdown("### Summary of Your Financial Activity")
        st.write(f"Your total incoming is **{total_incoming} EUR**, and your total outgoing is **{total_outgoing} EUR**.")
        st.write(f"Your net balance is **{balance} EUR**.")
