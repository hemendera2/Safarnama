import requests
import time
import statistics

BASE_URL = "http://localhost:5000/api/v1"

def benchmark_endpoint(name, url, method="GET", json=None, count=50):
    print(f"Benchmarking {name} ({url})...")
    latencies = []
    for _ in range(count):
        start = time.perf_counter()
        if method == "GET":
            requests.get(url)
        else:
            requests.post(url, json=json)
        latencies.append((time.perf_counter() - start) * 1000)
    
    print(f"  Avg: {statistics.mean(latencies):.2f}ms")
    print(f"  P95: {statistics.quantiles(latencies, n=20)[18]:.2f}ms")
    print(f"  P99: {statistics.quantiles(latencies, n=100)[98]:.2f}ms")

if __name__ == "__main__":
    try:
        benchmark_endpoint("Health Check", f"{BASE_URL}/health")
        benchmark_endpoint("Get Places (All)", f"{BASE_URL}/places/")
        benchmark_endpoint("Radius Search (50km)", f"{BASE_URL}/places/?lat=25.4&lon=92.5&radius=50")
        benchmark_endpoint("Discovery", f"{BASE_URL}/places/discovery")
    except Exception as e:
        print(f"Benchmark failed: {e}. Is the server running?")
