# Divvy Bike Share 2025: analysis report

## Business task

Identify behavioral differences between annual members and casual riders, then use the findings to guide conversion-focused marketing.

## Data and method

The project combines the twelve public 2025 Divvy trip-data files into a local SQLite warehouse. The analysis calculates trip duration from `started_at` and `ended_at`, removes durations outside the range `(0 minutes, 24 hours]`, and compares rider segments by volume, duration, weekday, month, bike type, and starting station.

Run `python scripts/analyze_divvy.py` from the repository root to regenerate every CSV and SVG in `outputs/`. Run the statements in `sql_queries/analysis_queries.sql` against the SQL Server copy of the data when using the SQL Server workflow.

## What has been completed

- Automated acquisition of every 2025 monthly source file.
- A SQLite warehouse (`data/divvy_2025.db`) containing 5,552,994 raw trips.
- Migration workflow to SQL Server (`Divvy_Capstone`, `trips_2025`).
- Reproducible analyses, tables, and charts generated from the SQLite warehouse.

## Results

Of 5,552,994 raw trips, 5,614 (0.10%) were excluded by the duration rule, leaving 5,547,380 valid rides.

| Rider type | Valid rides | Share of valid rides | Average ride length |
| --- | ---: | ---: | ---: |
| Annual member | 3,552,569 | 64.0% | 11.95 minutes |
| Casual rider | 1,994,811 | 36.0% | 19.13 minutes |

Members supplied most rides, while casual riders averaged 7.18 additional minutes per trip (about 60% longer). Ride volume was highest in August. This suggests seasonal conversion campaigns should prioritize high-demand summer periods and use messaging that recognizes longer, leisure-oriented casual trips.

The data table includes 53 rides that began on December 31, 2024, because of source-file timestamp boundaries. The monthly table retains them for transparency; they are too few to affect the 2025 interpretation.

## Interpretation guidance

Do not treat `member_casual` as a causal variable: the data describes observed behavior, not the effect of a campaign. Use the generated monthly and weekday summaries to target high-demand casual-rider windows, and validate any conversion offer with an A/B test before broad rollout.

## Recommended next step

Use casual-rider peaks from `outputs/monthly_summary.csv` and `outputs/weekday_summary.csv` to schedule a time-limited membership offer. Track offer exposure, conversion, and retained membership by cohort.
