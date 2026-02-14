import time

import requests
import logging
from fastapi import FastAPI, Request
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
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "path", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Request latency",
    ["method", "path"]
)


app = FastAPI()


# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        path=request.url.path
    ).observe(duration)

    return response


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health():
    return {"status": "ok"}



@app.post("/order")
def create_order(simulate: str = "none"):

    logger.info("creating order", extra={"simulate": simulate})

    # simulate latency
    if simulate == "slow":
        time.sleep(2)

    # simulate internal error
    if simulate == "error":
        logger.error("order internal failure")
        return Response(status_code=500)

    # call payment service
    try:
        response = requests.post("http://payment-service:8001/pay", timeout=3)

        if response.status_code != 200:
            logger.error("payment failed")
            return Response(status_code=502)

    except Exception as e:
        logger.error("payment service unreachable", extra={"error": str(e)})
        return Response(status_code=503)

    return {"status": "order created"}
