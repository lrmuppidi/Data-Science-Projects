import pandas as pd
from utils import get_connection

conn = get_connection()

warehouses = pd.read_sql_query("SELECT * FROM warehouses", conn)
drivers = pd.read_sql_query("SELECT * FROM drivers", conn)
vehicles = pd.read_sql_query("SELECT * FROM vehicles", conn)
routes = pd.read_sql_query("SELECT * FROM routes", conn)
shipments = pd.read_sql_query("SELECT * FROM shipments", conn)
deliveries = pd.read_sql_query("SELECT * FROM deliveries", conn)
feedback = pd.read_sql_query("SELECT * FROM feedback", conn)

shipments["shipment_dt"] = pd.to_datetime(shipments["shipment_dt"])
deliveries["actual_dt"] = pd.to_datetime(deliveries["actual_dt"])
feedback["feedback_dt"] = pd.to_datetime(feedback["feedback_dt"])

warehouses = warehouses.rename(columns={"name": "warehouse_name"})
drivers = drivers.rename(columns={"name": "driver_name", "rating": "driver_rating"})

feedback = feedback.drop_duplicates(subset="delivery_id")

master = deliveries.merge(shipments, on="shipment_id")
master = master.merge(feedback[["delivery_id", "rating", "feedback_dt"]], on="delivery_id", how="left")
master = master.merge(warehouses[["warehouse_id", "warehouse_name"]], on="warehouse_id")
master = master.merge(drivers[["driver_id", "driver_name", "experience", "driver_rating"]], on="driver_id")
master = master.merge(vehicles[["vehicle_id", "vehicle_type", "capacity_kg"]], on="vehicle_id")
master = master.merge(routes, on="route_id")

master["delivery_hours"] = (master["actual_dt"] - master["shipment_dt"]).dt.total_seconds() / 3600
master.loc[master["delivery_hours"] < 0, "delivery_hours"] = None   
master["delivery_days"] = master["delivery_hours"] / 24

master.loc[~master["status"].isin(["Delivered", "Delayed"]), "delay_hours"] = None

master["is_delayed"] = (master["delay_hours"] > 0).astype(int)

master["is_success"] = (master["status"] == "Delivered").astype(int)
master["is_completed"] = (master["status"] != "In-Transit").astype(int)

master["weight_category"] = pd.qcut(master["weight_kg"].rank(method="first"), 4,
                                    labels=["Light", "Medium", "Heavy", "Very Heavy"])
master["distance_category"] = pd.qcut(master["distance_km"].rank(method="first"), 4,
                                      labels=["Short", "Medium", "Long", "Very Long"])
master["experience_level"] = pd.cut(master["experience"], bins=[-1, 2, 5, 10, 100],
                                    labels=["Junior", "Mid", "Senior", "Expert"])  

master["ship_date"] = master["shipment_dt"].dt.strftime("%Y-%m-%d")
master["ship_month"] = master["shipment_dt"].dt.strftime("%Y-%m")
master["month_num"] = master["shipment_dt"].dt.month
master["quarter"] = master["shipment_dt"].dt.quarter
master["day_of_week"] = master["shipment_dt"].dt.day_name()
master["dow_num"] = master["shipment_dt"].dt.dayofweek    
master["hour"] = master["shipment_dt"].dt.hour

master["weight_category"] = master["weight_category"].astype(str)
master["distance_category"] = master["distance_category"].astype(str)
master["experience_level"] = master["experience_level"].astype(str)
master["shipment_dt"] = master["shipment_dt"].dt.strftime("%Y-%m-%d %H:%M:%S")
master["actual_dt"] = master["actual_dt"].dt.strftime("%Y-%m-%d %H:%M:%S")
master["feedback_dt"] = master["feedback_dt"].dt.strftime("%Y-%m-%d %H:%M:%S")

master.to_sql("delivery_master", conn, if_exists="replace", index=False)
conn.commit()
conn.close()

print("delivery_master table created:", master.shape)
print(master[["delivery_hours", "delay_hours", "is_delayed", "weight_category",
              "distance_category", "experience_level"]].head())
