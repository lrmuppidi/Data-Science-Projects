import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from utils import QUERIES_FILE, get_connection


def load_queries():
    """Read sql/analysis_queries.sql and return a dictionary like {"Q1": "SQL text", ...}"""
    queries = {}
    with open(QUERIES_FILE) as sql_file:
        text = sql_file.read()
    pieces = text.split("-- Q")[1:]           
    for piece in pieces:
        number = piece.split(":")[0]          
        queries["Q" + number] = "-- Q" + piece.strip().rstrip(";")
    return queries


QUERIES = load_queries()

st.set_page_config(page_title="LogiTrack Dashboard", layout="wide")
st.title("LogiTrack: Supply Chain & Logistics Performance")

conn = get_connection()


def get_options(column):
    """Get the unique values of a column from SQL (used to fill the sidebar filters)."""
    sql = "SELECT DISTINCT " + column + " AS value FROM delivery_master WHERE " + column + " IS NOT NULL ORDER BY value"
    return pd.read_sql_query(sql, conn)["value"].tolist()


def format_number(value, decimals=1, suffix=""):
    """Show N/A when the value is missing (NULL handling for KPIs)."""
    if pd.isna(value):
        return "N/A"
    return str(round(value, decimals)) + suffix



st.sidebar.header("Filters")

dates = pd.read_sql_query("SELECT MIN(ship_date) AS first_day, MAX(ship_date) AS last_day FROM delivery_master", conn)
first_day = pd.to_datetime(dates["first_day"].iloc[0]).date()
last_day = pd.to_datetime(dates["last_day"].iloc[0]).date()
date_range = st.sidebar.date_input("Shipment date range", value=(first_day, last_day))
if len(date_range) != 2:
    st.info("Please select both a start date and an end date.")
    st.stop()

chosen_status = st.sidebar.multiselect("Delivery status", get_options("status"))
chosen_warehouse = st.sidebar.multiselect("Warehouse", get_options("warehouse_name"))
chosen_route_type = st.sidebar.multiselect("Route type", get_options("route_type"))
chosen_driver = st.sidebar.multiselect("Driver", get_options("driver_name"))
chosen_vehicle = st.sidebar.multiselect("Vehicle type", get_options("vehicle_type"))
st.sidebar.caption("Leave a filter empty to include everything.")

where = "ship_date BETWEEN ? AND ?"
params = [str(date_range[0]), str(date_range[1])]

filter_list = [
    ("status", chosen_status),
    ("warehouse_name", chosen_warehouse),
    ("route_type", chosen_route_type),
    ("driver_name", chosen_driver),
    ("vehicle_type", chosen_vehicle),
]
for column, chosen_values in filter_list:
    if len(chosen_values) > 0:
        marks = ",".join(["?"] * len(chosen_values))          
        where = where + " AND " + column + " IN (" + marks + ")"
        params = params + chosen_values


def run_query(name):
    """Run one of the 10 queries from queries.py with the current filters applied."""
    sql = QUERIES[name].replace("{where}", where)
    return pd.read_sql_query(sql, conn, params=params)


detail = pd.read_sql_query("SELECT * FROM delivery_master WHERE " + where, conn, params=params)
if detail.empty:
    st.warning("No deliveries match the selected filters.")
    st.stop()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Business Overview", "Delivery Analysis", "Driver Performance",
    "Vehicle & Route Analysis", "Customer Feedback", "SQL Queries"])

with tab1:
    st.subheader("Business Overview")
    kpi = run_query("Q1").iloc[0]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Deliveries", int(kpi["total_deliveries"]))
    c2.metric("Total Shipments", int(kpi["total_shipments"]))
    c3.metric("Avg Delay (hours)", format_number(kpi["avg_delay_hours"], 2))
    c4.metric("Avg Rating (1-5)", format_number(kpi["avg_rating"], 2))
    c5.metric("Delivery Success Rate", format_number(kpi["success_rate_pct"], 1, "%"))

    with st.expander("KPI calculation rules"):
        st.write("- Total Deliveries: number of delivery records after filters")
        st.write("- Total Shipments: number of different shipment IDs")
        st.write("- Avg Delay Hours: average delay of Delivered/Delayed deliveries (Cancelled/In-Transit are NULL and ignored)")
        st.write("- Avg Rating: average of valid ratings 1-5 (deliveries without feedback are ignored)")
        st.write("- Success Rate: Delivered / all deliveries except In-Transit")

with tab2:
    st.subheader("Delivery Analysis")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.pie(run_query("Q7"), names="status", values="deliveries",
                               title="Delivery Status Distribution"))
    with right:
        st.plotly_chart(px.bar(run_query("Q2"), x="route_type", y="avg_delay_hours",
                               title="Average Delay by Route Type"))
    st.plotly_chart(px.line(run_query("Q5"), x="ship_month", y="deliveries", markers=True,
                            title="Monthly Delivery Trends"))
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.bar(run_query("Q4"), x="warehouse_name", y="avg_delay_hours",
                               title="Average Delay by Warehouse"))
    with right:
        st.plotly_chart(px.bar(run_query("Q10"), x="day_of_week", y="delay_rate_pct",
                               title="Delay Rate (%) by Day of Week"))

with tab3:
    st.subheader("Driver Performance")
    st.plotly_chart(px.bar(run_query("Q3"), x="avg_rating", y="driver_name", orientation="h",
                           title="Top 10 Drivers by Rating"))
    experience = run_query("Q9")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.bar(experience, x="experience_level", y="success_rate_pct",
                               title="Success Rate (%) by Experience Level"))
    with right:
        st.plotly_chart(px.bar(experience, x="experience_level", y="avg_rating",
                               title="Average Rating by Experience Level"))
    workload = detail.groupby("driver_name").size().reset_index(name="deliveries")
    st.plotly_chart(px.histogram(workload, x="deliveries", title="Driver Workload (deliveries per driver)"))

with tab4:
    st.subheader("Vehicle & Route Analysis")
    vehicles = run_query("Q6")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.bar(vehicles, x="vehicle_type", y="trips_per_vehicle",
                               title="Vehicle Utilization: Trips per Vehicle"))
    with right:
        st.plotly_chart(px.bar(vehicles, x="vehicle_type", y="avg_load_util_pct",
                               title="Average Load Utilization (%)"))

    detail["route"] = detail["origin_city"] + " to " + detail["dest_city"]
    route_summary = detail.groupby("route").agg(deliveries=("delivery_id", "count"),
                                                avg_delay=("delay_hours", "mean")).reset_index()
    route_summary = route_summary[route_summary["deliveries"] >= 5]
    route_summary = route_summary.sort_values("avg_delay", ascending=False).head(10)
    st.plotly_chart(px.bar(route_summary, x="avg_delay", y="route", orientation="h",
                           title="Route Comparison: 10 Slowest Routes (average delay hours)"))

    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.bar(run_query("Q8"), x="distance_category", y="avg_delay_hours",
                               title="Average Delay by Distance Category"))
    with right:
        st.plotly_chart(px.scatter(detail.dropna(subset=["delay_hours"]), x="distance_km", y="delay_hours",
                                   color="route_type", title="Distance vs Delay"))

with tab5:
    st.subheader("Customer Feedback")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.histogram(detail.dropna(subset=["rating"]), x="rating",
                                     title="Rating Distribution"))
    with right:
        st.plotly_chart(px.bar(run_query("Q7"), x="status", y="avg_rating",
                               title="Average Rating by Delivery Status"))
    st.plotly_chart(px.line(run_query("Q5"), x="ship_month", y="avg_rating", markers=True,
                            title="Rating Trend Over Time"))

with tab6:
    st.subheader("10 Key SQL Queries")
    st.caption("{where} is replaced by your sidebar filters. Current filter:")
    st.code(where, language="sql")
    for name in QUERIES:
        st.code(QUERIES[name], language="sql")

conn.close()
