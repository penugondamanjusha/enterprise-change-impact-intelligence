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

# Require to add anomalies into the system metrics
def inject_anomalies(df, anomaly_fraction=0.05):
    
    df = df.copy()
    df["is_injected_anomaly"] = 0

    anomaly_count = int(len(df) * anomaly_fraction)
    anomaly_indices = random.sample(range(len(df)), anomaly_count)

    df.loc[anomaly_indices, "response_time_ms"] *= 2
    df.loc[anomaly_indices, "error_rate_percent"] *= 5
    df.loc[anomaly_indices, "timeout_count"] += 5
    df.loc[anomaly_indices, "is_injected_anomaly"] = 1

    return df

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
    metrics_df = inject_anomalies(metrics_df)

    changes_df = generate_change_events(start_time, periods)

# Coverting the data frame to CSV files.

    metrics_df.to_csv("data/raw/system_metrics.csv", index=False)
    changes_df.to_csv("data/raw/change_events.csv", index=False)



