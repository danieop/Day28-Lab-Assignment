from datetime import datetime
import json
import os

from kafka import KafkaConsumer
import pandas as pd

try:
    from prefect import flow, task
except ImportError:
    def task(fn):
        return fn

    def flow(*_args, **_kwargs):
        def decorator(fn):
            return fn
        return decorator


@task
def consume_and_process():
    consumer = KafkaConsumer(
        "data.raw",
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092"),
        auto_offset_reset="earliest",
        consumer_timeout_ms=5000,
        value_deserializer=lambda message: json.loads(message.decode()),
    )
    records = [message.value for message in consumer]
    print(f"Consumed {len(records)} records from Kafka")
    return records


@task
def save_to_delta(records):
    if not records:
        print("No records to save")
        return

    df = pd.DataFrame(records)
    path = os.environ.get("DELTA_LAKE_PATH", "/opt/delta-lake/raw")
    os.makedirs(path, exist_ok=True)
    output = f"{path}/batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
    df.to_parquet(output)
    print(f"Saved {len(df)} records to Delta Lake at {output}")


@flow(name="Kafka to Delta Pipeline")
def kafka_to_delta_flow():
    records = consume_and_process()
    save_to_delta(records)


if __name__ == "__main__":
    kafka_to_delta_flow()
