import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import random

import warnings
warnings.filterwarnings('ignore')

#Generating timestamp for every 5 minutues for required number of periods
def generate_timestamps(start_time, periods, freq_minutes=5):
    return [start_time + timedelta(minutes=freq_minutes * i) for i in range(periods)]

#To generate system metrics for the required period.
def generate_system_metrics(start_time, periods):
    timestamps = generate_timestamps(start_time, periods)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "application_name": "CoreBankingApp",
        "environment": "Production",
        "response_time_ms": np.random.normal(200, 30, periods),
        "throughput_rpm": np.random.normal(1200, 100, periods),
        "cpu_usage_percent": np.random.normal(60, 10, periods),
        "memory_usage_percent": np.random.normal(65, 8, periods),
        "error_rate_percent": np.random.normal(0.5, 0.2, periods),
        "timeout_count": np.random.poisson(1, periods)#using poisson since it is a discrete event
    })

    df["response_time_ms"] += df["cpu_usage_percent"] * 1.5
    df["error_rate_percent"] += df["memory_usage_percent"] * 0.01
    return df

def inject_change_impact(metrics_df, changes_df):
    metrics_df = metrics_df.copy()
    metrics_df["is_injected_anomaly"] = 0

    for _, change in changes_df.iterrows():
        change_time = change["change_timestamp"]
        change_type = change["change_type"]

        
        if random.random() > 0.6:  # only 40% cause impact
            continue

        # Adding Delay
        delay_minutes = random.randint(5, 20)
        impact_start = change_time + timedelta(minutes=delay_minutes)

        
        impact_duration = 60
        impact_end = impact_start + timedelta(minutes=impact_duration)

        mask = (metrics_df["timestamp"] >= impact_start) & \
               (metrics_df["timestamp"] <= impact_end)

        severity = np.random.uniform(1.2, 2.0)

        if change_type == "Deployment":
            metrics_df.loc[mask, "response_time_ms"] *= severity
            metrics_df.loc[mask, "error_rate_percent"] *= severity * 2
            metrics_df.loc[mask, "timeout_count"] += int(severity * 3)

        elif change_type == "DB Change":
            metrics_df.loc[mask, "response_time_ms"] *= severity * 0.9
            metrics_df.loc[mask, "error_rate_percent"] *= severity * 1.8
            metrics_df.loc[mask, "timeout_count"] += int(severity * 2)

        elif change_type == "Config Update":
            metrics_df.loc[mask, "response_time_ms"] *= severity * 0.7
            metrics_df.loc[mask, "error_rate_percent"] *= severity * 1.5

        elif change_type == "Infra Scaling":
            # Sometimes improves system
            improvement = np.random.uniform(0.7, 0.95)
            metrics_df.loc[mask, "response_time_ms"] *= improvement
            metrics_df.loc[mask, "error_rate_percent"] *= improvement

        metrics_df.loc[mask, "is_injected_anomaly"] = 1

    return metrics_df

# To generate data for change events within the period.
def generate_change_events(start_time, periods):
    teams = ["Application Team", "Database Team", "Infrastructure Team"]
    change_types = ["Deployment", "Config Update", "DB Change", "Infra Scaling"]

    changes = []

    for i in range(int(periods * 0.1)):
        change_time = start_time + timedelta(minutes=random.randint(0, periods * 5))
        changes.append({
            "change_id": f"CHG-{1000 + i}",
            "change_timestamp": change_time,
            "change_type": random.choice(change_types),
            "affected_component": "CoreBankingApp",
            "owning_team": random.choice(teams),
            "environment": "Production",
            "change_description": "Planned system update"
        })

    return pd.DataFrame(changes)

if __name__ == "__main__":
    start_time = datetime.now() - timedelta(days=7)
    periods = 2016  # 7 days of 5-minute intervals

    metrics_df = generate_system_metrics(start_time, periods)
    changes_df = generate_change_events(start_time, periods)
    metrics_df = inject_change_impact(metrics_df, changes_df)

# Coverting the data frame to CSV files.

    metrics_df.to_csv("data/raw/system_metrics.csv", index=False)
    changes_df.to_csv("data/raw/change_events.csv", index=False)



