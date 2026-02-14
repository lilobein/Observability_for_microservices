import time
import random
import logging
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

REQUEST_COUNT = Counter(
    "payment_requests_total",
    "Total Payment Requests",
    ["status"]
)

REQUEST_LATENCY = Histogram(
    "payment_request_latency_seconds",
    "Payment latency"
)

app = FastAPI()


@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    REQUEST_LATENCY.observe(duration)
    REQUEST_COUNT.labels(status=response.status_code).inc()

    return response


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/pay")
def pay():
    simulate = random.choice(["ok", "slow", "error"])

    if simulate == "slow":
        time.sleep(1.5)

    if simulate == "error":
        logger.error("payment processing error")
        return Response(status_code=500)

    return {"status": "paid"}
