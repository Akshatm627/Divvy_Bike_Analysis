"""Create reproducible summaries for the 2025 Divvy Bike Share analysis.

Run from the repository root:
    python scripts/analyze_divvy.py

The script reads the local SQLite warehouse and writes small, Git-friendly
CSV summaries and SVG charts to outputs/. Source trip files are never changed.
"""

from __future__ import annotations

import csv
import html
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "divvy_2025.db"
OUTPUT = ROOT / "outputs"


VALID_RIDES = """
WITH valid_rides AS (
    SELECT
        *,
        (julianday(ended_at) - julianday(started_at)) * 24 * 60 AS ride_length_minutes
    FROM trips
    WHERE started_at IS NOT NULL
      AND ended_at IS NOT NULL
      AND (julianday(ended_at) - julianday(started_at)) * 24 * 60 > 0
      AND (julianday(ended_at) - julianday(started_at)) * 24 * 60 <= 1440
)
"""


QUERIES = {
    "rider_summary": VALID_RIDES + """
        SELECT member_casual AS rider_type,
               COUNT(*) AS rides,
               ROUND(AVG(ride_length_minutes), 2) AS average_ride_minutes,
               ROUND(SUM(ride_length_minutes) / 60.0, 2) AS total_ride_hours
        FROM valid_rides
        GROUP BY member_casual
        ORDER BY rides DESC;
    """,
    "weekday_summary": VALID_RIDES + """
        SELECT CASE strftime('%w', started_at)
                   WHEN '0' THEN 'Sunday' WHEN '1' THEN 'Monday'
                   WHEN '2' THEN 'Tuesday' WHEN '3' THEN 'Wednesday'
                   WHEN '4' THEN 'Thursday' WHEN '5' THEN 'Friday'
                   WHEN '6' THEN 'Saturday' END AS day_of_week,
               member_casual AS rider_type,
               COUNT(*) AS rides,
               ROUND(AVG(ride_length_minutes), 2) AS average_ride_minutes
        FROM valid_rides
        GROUP BY strftime('%w', started_at), member_casual
        ORDER BY CAST(strftime('%w', started_at) AS INTEGER), rider_type;
    """,
    "monthly_summary": VALID_RIDES + """
        SELECT strftime('%Y-%m', started_at) AS month,
               member_casual AS rider_type,
               COUNT(*) AS rides,
               ROUND(AVG(ride_length_minutes), 2) AS average_ride_minutes
        FROM valid_rides
        GROUP BY month, member_casual
        ORDER BY month, rider_type;
    """,
    "bike_type_summary": VALID_RIDES + """
        SELECT rideable_type,
               member_casual AS rider_type,
               COUNT(*) AS rides,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY member_casual), 2) AS rider_type_share_pct
        FROM valid_rides
        GROUP BY rideable_type, member_casual
        ORDER BY rider_type, rides DESC;
    """,
    "top_start_stations": VALID_RIDES + """
        SELECT member_casual AS rider_type,
               COALESCE(start_station_name, 'Unknown') AS start_station_name,
               COUNT(*) AS rides
        FROM valid_rides
        GROUP BY member_casual, COALESCE(start_station_name, 'Unknown')
        ORDER BY rider_type, rides DESC
        LIMIT 20;
    """,
}


def write_csv(path: Path, rows: list[sqlite3.Row]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(dict(row) for row in rows)


def bar_chart(path: Path, title: str, labels: list[str], values: list[float], color: str = "#2563eb") -> None:
    """Write a simple dependency-free horizontal SVG bar chart."""
    width, row_height, left, right, top = 900, 34, 210, 120, 80
    height = top + len(labels) * row_height + 55
    maximum = max(values) if values else 1
    bars = []
    for index, (label, value) in enumerate(zip(labels, values)):
        y = top + index * row_height
        bar_width = (width - left - right) * value / maximum
        bars.append(
            f'<text x="{left - 12}" y="{y + 20}" text-anchor="end">{html.escape(label)}</text>'
            f'<rect x="{left}" y="{y + 5}" width="{bar_width:.1f}" height="20" rx="3" fill="{color}"/>'
            f'<text x="{left + bar_width + 8:.1f}" y="{y + 20}">{value:,.0f}</text>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>text {{ font: 14px Arial, sans-serif; fill: #172033; }} .title {{ font-size: 22px; font-weight: 700; }}</style>
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text class="title" x="30" y="40">{html.escape(title)}</text>
  {''.join(bars)}
</svg>'''
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    if not DATABASE.exists():
        raise SystemExit(f"Database not found: {DATABASE}")
    OUTPUT.mkdir(exist_ok=True)
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    try:
        total_rides = connection.execute("SELECT COUNT(*) AS count FROM trips").fetchone()["count"]
        invalid_rides = connection.execute(
            """SELECT COUNT(*) AS count FROM trips
               WHERE started_at IS NULL OR ended_at IS NULL
                  OR (julianday(ended_at) - julianday(started_at)) * 24 * 60 <= 0
                  OR (julianday(ended_at) - julianday(started_at)) * 24 * 60 > 1440"""
        ).fetchone()["count"]
        summaries = {name: connection.execute(query).fetchall() for name, query in QUERIES.items()}
    finally:
        connection.close()

    for name, rows in summaries.items():
        write_csv(OUTPUT / f"{name}.csv", rows)

    rider_rows = summaries["rider_summary"]
    bar_chart(OUTPUT / "rides_by_rider_type.svg", "Valid rides by rider type", [r["rider_type"].title() for r in rider_rows], [r["rides"] for r in rider_rows], "#0f766e")

    month_totals: dict[str, int] = {}
    for row in summaries["monthly_summary"]:
        month_totals[row["month"]] = month_totals.get(row["month"], 0) + row["rides"]
    bar_chart(OUTPUT / "monthly_rides.svg", "Valid rides by month", list(month_totals), list(month_totals.values()), "#7c3aed")

    quality = OUTPUT / "data_quality_summary.csv"
    with quality.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerows([
            {"metric": "raw_rides", "value": total_rides},
            {"metric": "excluded_invalid_duration_rides", "value": invalid_rides},
            {"metric": "valid_rides", "value": total_rides - invalid_rides},
        ])
    print(f"Wrote summaries and charts to {OUTPUT}")


if __name__ == "__main__":
    main()
