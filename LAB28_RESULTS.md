# Lab 28 Results

Run date: 2026-05-18

## Screenshots

- Prefect flow runs: `screenshots/prefect_ui.png`
- API Gateway health check: `screenshots/api_gateway.png`
- Grafana dashboard: `screenshots/grafana_dashboard.png`
- Kaggle kernel status: `screenshots/kaggle_kernel_status.png`
- Smoke tests: `screenshots/smoke_tests_results.png`
- Production readiness: `screenshots/production_readiness.png`

## Verification Summary

- Docker Compose stack: all services running.
- Kaggle kernel: `quangngnguyn/lab28-vllm-ngrok-serving` is `RUNNING`.
- Kaggle/ngrok serving URL: `https://thermodynamic-helicoidally-waylon.ngrok-free.dev`.
- API Gateway chat call returned a Kaggle/ngrok response with latency under 1 second.
- Smoke tests: `8 passed`.
- Production readiness score: `10/10 = 100%`.

## Commands Used

```powershell
docker compose up -d --build
python scripts\01_ingest_to_kafka.py
$env:KAFKA_BOOTSTRAP_SERVERS='localhost:9092'; $env:DELTA_LAKE_PATH='delta-lake/raw'; python prefect\flows\kafka_to_delta.py
python scripts\03_delta_to_feast.py
$env:EMBED_NGROK_URL='https://thermodynamic-helicoidally-waylon.ngrok-free.dev'; python scripts\05_embed_to_qdrant.py
python -m pytest smoke-tests\ -v
python scripts\production_readiness_check.py
```

## Notes

The local mock service has been removed. Docker Compose uses real `VLLM_NGROK_URL` and `EMBED_NGROK_URL` values from the Kaggle notebook in `kaggle-lab28/`.
