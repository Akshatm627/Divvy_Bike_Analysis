# Data dictionary

Source: [Divvy trip data](https://divvy-tripdata.s3.amazonaws.com/index.html). The local warehouse stores 2025 monthly files in one `trips` table.

| Field | Description |
| --- | --- |
| `ride_id` | Unique trip identifier. |
| `rideable_type` | Bike category, such as classic, electric, or docked. |
| `started_at`, `ended_at` | Trip start and end timestamp. |
| `start_station_name`, `end_station_name` | Origin and destination station label; may be blank. |
| `start_station_id`, `end_station_id` | Origin and destination station identifier; may be blank. |
| `start_lat`, `start_lng`, `end_lat`, `end_lng` | Start and end coordinates. |
| `member_casual` | Rider segment: annual member or casual rider. |
| `ride_length_minutes` | Derived field: end time minus start time. It is calculated during analysis, not stored in the raw source. |

## Data-quality rule

Analysis excludes rides whose duration is zero/negative or exceeds 24 hours. These records are likely clock, operational, or bike-recovery anomalies and would distort typical-ride metrics.
