import pandas as pd
import os 
from datetime import timedelta
from pathlib import Path


def compute_change_impact(metrics_df, changes_df):
    results = []

    for _, change in changes_df.iterrows():
        change_time = change["change_timestamp"]

        # BEFORE window (30 mins)
        pre_start = change_time - timedelta(minutes=30)
        pre_end = change_time

        # AFTER window (30 mins)
        post_start = change_time
        post_end = change_time + timedelta(minutes=30)

        pre_data = metrics_df[
            (metrics_df["timestamp"] >= pre_start) &
            (metrics_df["timestamp"] < pre_end)
        ]

        post_data = metrics_df[
            (metrics_df["timestamp"] >= post_start) &
            (metrics_df["timestamp"] <= post_end)
        ]

        if len(pre_data) == 0 or len(post_data) == 0:
            continue

        # Averages
        pre_rt = pre_data["response_time_ms"].mean()
        post_rt = post_data["response_time_ms"].mean()

        pre_err = pre_data["error_rate_percent"].mean()
        post_err = post_data["error_rate_percent"].mean()

        pre_timeout = pre_data["timeout_count"].mean()
        post_timeout = post_data["timeout_count"].mean()

        # Deltas
        delta_rt = post_rt - pre_rt
        delta_err = post_err - pre_err
        delta_timeout = post_timeout - pre_timeout

        # Impact label
        impact = 1 if (
            delta_rt > 40 or
            delta_err > 0.8 or
            delta_timeout > 2
        ) else 0

        results.append({
            "change_id": change["change_id"],
            "change_type": change["change_type"],
            "owning_team": change["owning_team"],
            "environment": change["environment"],
            "delta_response_time": delta_rt,
            "delta_error_rate": delta_err,
            "delta_timeout": delta_timeout,
            "impact": impact
        })

    return pd.DataFrame(results)


def main():
   
   BASE_DIR = Path(__file__).resolve().parents[2]
   RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
   OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed")
   os.makedirs(OUTPUT_PATH, exist_ok=True)
   
   METRICS_FILE = os.path.join(RAW_DATA_PATH, "system_metrics.csv")
   CHANGES_FILE = os.path.join(RAW_DATA_PATH, "change_events.csv")
   OUTPUT_FILE = os.path.join(OUTPUT_PATH, "change_impact.csv")

    # Load
   metrics_df = pd.read_csv(METRICS_FILE)
   changes_df = pd.read_csv(CHANGES_FILE)

    # Clean
   metrics_df = metrics_df.dropna().drop_duplicates()
   changes_df = changes_df.dropna().drop_duplicates()

    # Convert timestamps
   metrics_df["timestamp"] = pd.to_datetime(metrics_df["timestamp"])
   changes_df["change_timestamp"] = pd.to_datetime(changes_df["change_timestamp"])

    # Compute impact
   impact_df = compute_change_impact(metrics_df, changes_df)

    # Save output
   impact_df.to_csv("data/processed/change_impact.csv", index=False)



if __name__ == "__main__":
    main()