import os
import pandas as pd
from utils import RAW_DIR, CLEAN_DIR, SCHEMA_FILE, get_connection

warehouses = pd.read_csv(RAW_DIR + "logitrack_warehouses_expanded.csv")
drivers = pd.read_csv(RAW_DIR + "logitrack_drivers_expanded.csv")
vehicles = pd.read_csv(RAW_DIR + "logitrack_vehicles_expanded.csv")
routes = pd.read_csv(RAW_DIR + "logitrack_routes_expanded.csv")
shipments = pd.read_csv(RAW_DIR + "logitrack_shipments_expanded.csv")
deliveries = pd.read_csv(RAW_DIR + "logitrack_deliveries_expanded.csv")
feedback = pd.read_csv(RAW_DIR + "logitrack_feedback_expanded.csv")

raw_tables = {
    "warehouses": warehouses, "drivers": drivers, "vehicles": vehicles, "routes": routes,
    "shipments": shipments, "deliveries": deliveries, "feedback": feedback,
}
rows_before = {}
for name in raw_tables:
    rows_before[name] = len(raw_tables[name])

for name in raw_tables:
    df = raw_tables[name]
    id_column = df.columns[0]  
    print("\n=====", name, "=====")
    print("Rows, columns :", df.shape)
    print(df.dtypes)
    print("Missing values per column:")
    print(df.isna().sum())
    print("Duplicate rows :", df.duplicated().sum())
    print("Duplicate IDs  :", df[id_column].duplicated().sum())

print("\nDelay hours summary (look for negative or very large values):")
print(deliveries["delay_hours"].describe())

warehouses["name"] = warehouses["name"].str.strip()
drivers["name"] = drivers["name"].str.strip()
vehicles["vehicle_type"] = vehicles["vehicle_type"].str.strip().str.title()
vehicles["fuel_type"] = vehicles["fuel_type"].str.strip().str.title()
vehicles["status"] = vehicles["status"].str.strip().str.title()
routes["route_type"] = routes["route_type"].str.strip().str.title()
shipments["priority"] = shipments["priority"].str.strip().str.title()
deliveries["status"] = deliveries["status"].str.strip().str.title()
deliveries["status"] = deliveries["status"].replace("In Transit", "In-Transit")

drivers["join_date"] = pd.to_datetime(drivers["join_date"], errors="coerce")
shipments["shipment_dt"] = pd.to_datetime(shipments["shipment_dt"], errors="coerce")
deliveries["actual_dt"] = pd.to_datetime(deliveries["actual_dt"], errors="coerce")
feedback["feedback_dt"] = pd.to_datetime(feedback["feedback_dt"], errors="coerce")

warehouses = warehouses.drop_duplicates(subset="warehouse_id")
drivers = drivers.drop_duplicates(subset="driver_id")
vehicles = vehicles.drop_duplicates(subset="vehicle_id")
routes = routes.drop_duplicates(subset="route_id")
shipments = shipments.drop_duplicates(subset="shipment_id")
deliveries = deliveries.drop_duplicates(subset="delivery_id")
feedback = feedback.drop_duplicates(subset="feedback_id")

drivers.loc[drivers["experience"] < 0, "experience"] = 0
drivers["experience"] = drivers["experience"].fillna(drivers["experience"].median())
drivers["experience"] = drivers["experience"].round().astype(int)
drivers.loc[(drivers["rating"] < 1) | (drivers["rating"] > 5), "rating"] = None
drivers["rating"] = drivers["rating"].fillna(drivers["rating"].median())

routes = routes[routes["distance_km"] > 0]

shipments["priority"] = shipments["priority"].fillna("Medium")
shipments = shipments[shipments["weight_kg"] > 0]
shipments = shipments[shipments["shipment_dt"].notna()]
shipments = shipments[shipments["warehouse_id"].isin(warehouses["warehouse_id"])]
shipments = shipments[shipments["driver_id"].isin(drivers["driver_id"])]
shipments = shipments[shipments["vehicle_id"].isin(vehicles["vehicle_id"])]
shipments = shipments[shipments["route_id"].isin(routes["route_id"])]

deliveries.loc[deliveries["delay_hours"] < 0, "delay_hours"] = 0
deliveries["delay_hours"] = deliveries["delay_hours"].fillna(0)
deliveries = deliveries[deliveries["shipment_id"].isin(shipments["shipment_id"])]

feedback = feedback[(feedback["rating"] >= 1) & (feedback["rating"] <= 5)]
feedback = feedback[feedback["delivery_id"].isin(deliveries["delivery_id"])].copy()
feedback["rating"] = feedback["rating"].astype(int)
feedback["comment"] = feedback["comment"].fillna("No comment")

cleaned_tables = {
    "warehouses": warehouses, "drivers": drivers, "vehicles": vehicles, "routes": routes,
    "shipments": shipments, "deliveries": deliveries, "feedback": feedback,
}
os.makedirs(CLEAN_DIR, exist_ok=True)
print("\nRows before -> after cleaning")
for name in cleaned_tables:
    cleaned_tables[name].to_csv(CLEAN_DIR + name + ".csv", index=False)
    print(name, ":", rows_before[name], "->", len(cleaned_tables[name]))

conn = get_connection()   
with open(SCHEMA_FILE) as schema_file:           
    conn.executescript(schema_file.read())

for name in cleaned_tables:
    cleaned_tables[name].to_sql(name, conn, if_exists="append", index=False)
conn.commit()

print("\nRows stored in the database:")
for name in cleaned_tables:
    count = conn.execute("SELECT COUNT(*) FROM " + name).fetchone()[0]
    print(name, ":", count)
conn.close()
