This project uses Prometheus to monitor the Products API and make sure it stays online.

Monitoring was added using a health endpoint, a metrics endpoint, Prometheus, Grafana, Docker health checks, and Jenkins checks. The /health endpoint is used to confirm that the API is running. The /metrics endpoint provides data for Prometheus to collect. Prometheus gathers this data, and Grafana shows it in charts. A Docker health check is included to help make sure the container stays running. Jenkins is also used to check that the API starts correctly.

The main files that were changed are app/main.py, app/routes.py, Dockerfile, monitoring/prometheus.yml, and docker-compose.monitoring.yml.

1. To run the project, first start the FastAPI app with:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
2. Then start Prometheus and Grafana with:
docker compose -f docker-compose.monitoring.yml up -d

After that, the following pages can be opened in a browser:
Prometheus at http://localhost:9090
Grafana at http://localhost:3000
Health endpoint at http://localhost:8000/health
Metrics endpoint at http://localhost:8000/metrics
Swagger documentation at http://localhost:8000/docs

The Grafana login details are username admin and password admin.

To connect Grafana to Prometheus, add Prometheus as a data source and use either http://prometheus:9090 or http://localhost:9090.

Some example queries that can be used in Prometheus or Grafana are:
request_count_total
rate(request_count_total[1m])
request_latency_seconds_count
requests_in_progress

The project also includes screenshots of the health endpoint, the metrics endpoint, and the get all products API endpoint. A Grafana dashboard screenshot can be added later when it is ready.

The tests were run using:
python -m unittest discover -s tests -p "test_*.py" -v
The result was that 10 tests ran successfully.

