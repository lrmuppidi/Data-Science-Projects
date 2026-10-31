DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS deliveries;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS drivers;
DROP TABLE IF EXISTS warehouses;

CREATE TABLE warehouses (
    warehouse_id INT PRIMARY KEY,
    name VARCHAR(100), city VARCHAR(50), state VARCHAR(50), capacity INT
);
CREATE TABLE drivers (
    driver_id INT PRIMARY KEY,
    name VARCHAR(100), experience INT, rating FLOAT, join_date DATE
);
CREATE TABLE vehicles (
    vehicle_id INT PRIMARY KEY,
    vehicle_type VARCHAR(20), capacity_kg INT, fuel_type VARCHAR(20), status VARCHAR(20)
);
CREATE TABLE routes (
    route_id INT PRIMARY KEY,
    origin_city VARCHAR(50), dest_city VARCHAR(50), distance_km FLOAT, route_type VARCHAR(20)
);
CREATE TABLE shipments (
    shipment_id INT PRIMARY KEY,
    warehouse_id INT, driver_id INT, vehicle_id INT, route_id INT,
    shipment_dt DATETIME, weight_kg FLOAT, priority VARCHAR(10),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    FOREIGN KEY (driver_id)    REFERENCES drivers(driver_id),
    FOREIGN KEY (vehicle_id)   REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (route_id)     REFERENCES routes(route_id)
);
CREATE TABLE deliveries (
    delivery_id INT PRIMARY KEY,
    shipment_id INT, actual_dt DATETIME, status VARCHAR(20), delay_hours FLOAT,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
);
CREATE TABLE feedback (
    feedback_id INT PRIMARY KEY,
    delivery_id INT, rating INT, comment TEXT, feedback_dt DATE,
    FOREIGN KEY (delivery_id) REFERENCES deliveries(delivery_id)
);
