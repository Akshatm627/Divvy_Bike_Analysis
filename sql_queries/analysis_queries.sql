-- Divvy Bike Share: reproducible analysis queries for SQL Server.
-- Run after loading raw trip records into dbo.trips_2025.

WITH valid_rides AS (
    SELECT *, DATEDIFF_BIG(second, started_at, ended_at) / 60.0 AS ride_length_minutes
    FROM dbo.trips_2025
    WHERE DATEDIFF_BIG(second, started_at, ended_at) BETWEEN 1 AND 86400
)
SELECT member_casual AS rider_type,
       COUNT(*) AS rides,
       ROUND(AVG(ride_length_minutes), 2) AS average_ride_minutes
FROM valid_rides
GROUP BY member_casual
ORDER BY rides DESC;

-- Ride volume and average duration by day of week.
WITH valid_rides AS (
    SELECT *, DATEDIFF_BIG(second, started_at, ended_at) / 60.0 AS ride_length_minutes
    FROM dbo.trips_2025
    WHERE DATEDIFF_BIG(second, started_at, ended_at) BETWEEN 1 AND 86400
)
SELECT DATENAME(weekday, started_at) AS day_of_week,
       member_casual AS rider_type,
       COUNT(*) AS rides,
       ROUND(AVG(ride_length_minutes), 2) AS average_ride_minutes
FROM valid_rides
GROUP BY DATENAME(weekday, started_at), DATEPART(weekday, started_at), member_casual
ORDER BY DATEPART(weekday, started_at), rider_type;

-- Monthly seasonality by rider type.
WITH valid_rides AS (
    SELECT *, DATEDIFF_BIG(second, started_at, ended_at) / 60.0 AS ride_length_minutes
    FROM dbo.trips_2025
    WHERE DATEDIFF_BIG(second, started_at, ended_at) BETWEEN 1 AND 86400
)
SELECT FORMAT(started_at, 'yyyy-MM') AS month,
       member_casual AS rider_type,
       COUNT(*) AS rides,
       ROUND(AVG(ride_length_minutes), 2) AS average_ride_minutes
FROM valid_rides
GROUP BY FORMAT(started_at, 'yyyy-MM'), member_casual
ORDER BY month, rider_type;
