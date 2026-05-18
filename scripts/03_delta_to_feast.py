import glob
import json

import pandas as pd
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def load_from_delta_and_push_feast():
    files = glob.glob("delta-lake/raw/*.parquet")
    if not files:
        print("No data in Delta Lake yet")
        return

    df = pd.concat([pd.read_parquet(file) for file in files])
    print(f"Loaded {len(df)} records from Delta Lake")

    for _, row in df.iterrows():
        feature_key = f"feature:{row['id']}"
        r.set(
            feature_key,
            json.dumps(
                {
                    "text": row["text"],
                    "timestamp": row.get("timestamp", 0),
                    "processed": True,
                }
            ),
        )

    print(f"Integration 3+4 OK: Delta Lake -> Feast (Redis) - {len(df)} features stored")


load_from_delta_and_push_feast()
