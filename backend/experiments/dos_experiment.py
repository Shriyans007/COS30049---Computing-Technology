"""Run actual HTTP baseline/protected overload measurements on localhost."""

import argparse
import asyncio
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from statistics import mean, median

import httpx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
TEXT = " ".join(
    "Furthermore, this comprehensive analysis demonstrates a robust and systematic approach."
    for _ in range(70)
)


async def wait_for_server(base_url: str) -> None:
    async with httpx.AsyncClient(timeout=1, trust_env=False) as client:
        for _ in range(80):
            try:
                if (await client.get(f"{base_url}/api/v1/health")).status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            await asyncio.sleep(0.1)
    raise RuntimeError("Experiment server did not become ready.")


async def measure_mode(mode: str, requests: int, port: int) -> tuple[list[dict[str, object]], dict[str, object]]:
    environment = os.environ.copy()
    environment.update(
        {
            "A3_EXPERIMENT_MODE": "true",
            "A3_DOS_PROTECTION_ENABLED": "true" if mode == "protected" else "false",
            "A3_INFERENCE_TEST_DELAY_MS": "250",
            "A3_RATE_LIMIT_REQUESTS": "1000",
            "A3_MAX_CONCURRENT_INFERENCES": "2",
            "A3_INFERENCE_QUEUE_TIMEOUT_SECONDS": "0.03",
        }
    )
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        await wait_for_server(base_url)
        start_gate = asyncio.Event()

        async def one_request(number: int, client: httpx.AsyncClient) -> dict[str, object]:
            await start_gate.wait()
            started = time.perf_counter()
            response = await client.post(f"{base_url}/api/v1/predict", json={"text": TEXT})
            return {
                "mode": mode,
                "request": number,
                "status": response.status_code,
                "elapsed_ms": round((time.perf_counter() - started) * 1_000, 3),
            }

        async with httpx.AsyncClient(timeout=30, trust_env=False) as client:
            tasks = [asyncio.create_task(one_request(number, client)) for number in range(1, requests + 1)]
            start_gate.set()
            await asyncio.sleep(0.04)
            health_started = time.perf_counter()
            health = await client.get(f"{base_url}/api/v1/health")
            health_ms = (time.perf_counter() - health_started) * 1_000
            rows = await asyncio.gather(*tasks)
        elapsed = [float(row["elapsed_ms"]) for row in rows]
        statuses: dict[str, int] = {}
        for row in rows:
            key = str(row["status"])
            statuses[key] = statuses.get(key, 0) + 1
        summary = {
            "mode": mode,
            "total_requests": requests,
            "status_counts": statuses,
            "successful_requests": statuses.get("200", 0),
            "rejected_requests": statuses.get("503", 0),
            "mean_response_ms": mean(elapsed),
            "median_response_ms": median(elapsed),
            "maximum_response_ms": max(elapsed),
            "health_status_during_load": health.status_code,
            "health_response_ms_during_load": health_ms,
            "controlled_cost_note": "A 250 ms local experiment-only delay makes inference cost repeatable.",
        }
        return rows, summary
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


async def run(requests: int) -> dict[str, object]:
    all_rows = []
    summaries = []
    for mode, port in (("baseline", 8011), ("protected", 8012)):
        rows, summary = await measure_mode(mode, requests, port)
        all_rows.extend(rows)
        summaries.append(summary)
    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / "dos_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)
    combined = {
        "method": "Concurrent HTTP POST requests against the real FastAPI endpoint",
        "baseline": summaries[0],
        "protected": summaries[1],
        "interpretation": (
            "Baseline accepts all concurrent inference work. Protected mode bounds work and rejects "
            "excess requests with HTTP 503 while the lightweight health route remains responsive."
        ),
    }
    (RESULTS / "dos_summary.json").write_text(json.dumps(combined, indent=2), encoding="utf-8")
    return combined


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests", type=int, default=20)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.requests)), indent=2))


if __name__ == "__main__":
    main()
