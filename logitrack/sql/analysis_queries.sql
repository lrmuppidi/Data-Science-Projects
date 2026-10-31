-- The 10 SQL queries used by the Streamlit dashboard.

-- Q1: Overall delivery performance
SELECT COUNT(*) AS total_deliveries,
       COUNT(DISTINCT shipment_id) AS total_shipments,
       ROUND(AVG(delay_hours), 2) AS avg_delay_hours,
       ROUND(AVG(rating), 2) AS avg_rating,
       ROUND(100.0 * SUM(is_success) / NULLIF(SUM(is_completed), 0), 1) AS success_rate_pct
FROM delivery_master
WHERE {where};

-- Q2: Average delay by route type
SELECT route_type,
       COUNT(*) AS deliveries,
       ROUND(AVG(delay_hours), 2) AS avg_delay_hours,
       ROUND(100.0 * SUM(is_delayed) / NULLIF(COUNT(delay_hours), 0), 1) AS delay_rate_pct
FROM delivery_master
WHERE {where}
GROUP BY route_type
ORDER BY avg_delay_hours DESC;

-- Q3: Top performing drivers (CTE + window function + HAVING)
WITH driver_stats AS (
    SELECT driver_id, driver_name,
           COUNT(*) AS deliveries,
           ROUND(AVG(rating), 2) AS avg_rating,
           ROUND(100.0 * SUM(is_success) / NULLIF(SUM(is_completed), 0), 1) AS success_rate_pct
    FROM delivery_master
    WHERE {where}
    GROUP BY driver_id, driver_name
    HAVING COUNT(*) >= 5
)
SELECT RANK() OVER (ORDER BY avg_rating DESC, success_rate_pct DESC) AS rank_no,
       driver_stats.*
FROM driver_stats
ORDER BY rank_no
LIMIT 10;

-- Q4: Delivery performance by warehouse (JOIN with the warehouses table)
SELECT m.warehouse_name,
       w.state,
       COUNT(*) AS deliveries,
       ROUND(1000.0 * COUNT(*) / NULLIF(w.capacity, 0), 1) AS deliveries_per_1000_capacity,
       ROUND(100.0 * SUM(m.is_success) / NULLIF(SUM(m.is_completed), 0), 1) AS success_rate_pct,
       ROUND(AVG(m.delay_hours), 2) AS avg_delay_hours,
       ROUND(AVG(m.rating), 2) AS avg_rating
FROM delivery_master m
INNER JOIN warehouses w ON w.warehouse_id = m.warehouse_id
WHERE {where}
GROUP BY m.warehouse_name, w.state, w.capacity
ORDER BY success_rate_pct DESC;

-- Q5: Monthly delivery trends
SELECT ship_month,
       COUNT(*) AS deliveries,
       ROUND(100.0 * SUM(is_delayed) / NULLIF(COUNT(delay_hours), 0), 1) AS delay_rate_pct,
       ROUND(AVG(delay_hours), 2) AS avg_delay_hours,
       ROUND(AVG(rating), 2) AS avg_rating
FROM delivery_master
WHERE {where}
GROUP BY ship_month
ORDER BY ship_month;

-- Q6: Vehicle utilization
SELECT vehicle_type,
       COUNT(DISTINCT vehicle_id) AS vehicles,
       COUNT(*) AS trips,
       ROUND(1.0 * COUNT(*) / COUNT(DISTINCT vehicle_id), 1) AS trips_per_vehicle,
       ROUND(AVG(100.0 * weight_kg / NULLIF(capacity_kg, 0)), 1) AS avg_load_util_pct,
       ROUND(AVG(delay_hours), 2) AS avg_delay_hours
FROM delivery_master
WHERE {where}
GROUP BY vehicle_type
ORDER BY trips_per_vehicle DESC;

-- Q7: Rating by delivery status
SELECT status,
       COUNT(*) AS deliveries,
       COUNT(rating) AS rated_deliveries,
       ROUND(AVG(rating), 2) AS avg_rating
FROM delivery_master
WHERE {where}
GROUP BY status
ORDER BY avg_rating DESC;

-- Q8: Delay analysis by distance category
SELECT distance_category,
       COUNT(*) AS deliveries,
       ROUND(AVG(delay_hours), 2) AS avg_delay_hours,
       ROUND(100.0 * SUM(is_delayed) / NULLIF(COUNT(delay_hours), 0), 1) AS delay_rate_pct
FROM delivery_master
WHERE {where}
GROUP BY distance_category
ORDER BY MIN(distance_km);

-- Q9: Driver performance by experience level
SELECT experience_level,
       COUNT(DISTINCT driver_id) AS drivers,
       COUNT(*) AS deliveries,
       ROUND(100.0 * SUM(is_success) / NULLIF(SUM(is_completed), 0), 1) AS success_rate_pct,
       ROUND(AVG(delay_hours), 2) AS avg_delay_hours,
       ROUND(AVG(rating), 2) AS avg_rating
FROM delivery_master
WHERE {where}
GROUP BY experience_level
ORDER BY MIN(experience);

-- Q10: Day of week analysis
SELECT day_of_week,
       COUNT(*) AS deliveries,
       ROUND(100.0 * SUM(is_delayed) / NULLIF(COUNT(delay_hours), 0), 1) AS delay_rate_pct,
       ROUND(AVG(delay_hours), 2) AS avg_delay_hours
FROM delivery_master
WHERE {where}
GROUP BY day_of_week
ORDER BY MIN(dow_num);
