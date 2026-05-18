import subprocess

import redis
import requests

results = {}


def check(name, fn):
    try:
        fn()
        results[name] = "PASS"
        print(f"  [PASS] {name}")
    except Exception as exc:
        results[name] = f"FAIL: {exc}"
        print(f"  [FAIL] {name}: {exc}")


print("\n=== RELIABILITY ===")
check("Health check endpoint", lambda: requests.get("http://localhost:8000/health", timeout=10).raise_for_status())
check("API Gateway responds", lambda: requests.get("http://localhost:8000/docs", timeout=10).raise_for_status())

print("\n=== OBSERVABILITY ===")
check("Prometheus up", lambda: requests.get("http://localhost:9090/-/healthy", timeout=10).raise_for_status())
check("Grafana up", lambda: requests.get("http://localhost:3000/api/health", timeout=10).raise_for_status())
check("Metrics endpoint exposed", lambda: requests.get("http://localhost:8000/metrics", timeout=10).raise_for_status())

print("\n=== SECURITY ===")


def check_unauthorized():
    response = requests.get("http://localhost:8000/admin", timeout=10)
    assert response.status_code in [401, 403, 404]


check("Unauthorized request rejected", check_unauthorized)

print("\n=== VECTOR STORE ===")
check("Qdrant healthy", lambda: requests.get("http://localhost:6333/healthz", timeout=10).raise_for_status())


def check_collection_exists():
    response = requests.get("http://localhost:6333/collections/documents", timeout=10)
    response.raise_for_status()
    assert response.json()["result"]["points_count"] > 0


check("Collection exists", check_collection_exists)

print("\n=== FEATURE STORE ===")
check("Redis reachable", lambda: redis.Redis(host="localhost", port=6379).ping())

print("\n=== KAFKA ===")


def check_kafka_topics():
    service_id = subprocess.run(
        ["docker", "compose", "ps", "-q", "kafka"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    result = subprocess.run(
        [
            "docker",
            "exec",
            service_id,
            "kafka-topics",
            "--list",
            "--bootstrap-server",
            "localhost:9092",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "data.raw" in result.stdout


check("Kafka topics exist", check_kafka_topics)

passed = sum(1 for value in results.values() if value == "PASS")
total = len(results)
score = (passed / total) * 100
print(f"\n{'=' * 40}")
print(f"Production Readiness Score: {passed}/{total} = {score:.0f}%")
print(f"Target: >80% - Status: {'READY' if score >= 80 else 'NOT READY'}")
